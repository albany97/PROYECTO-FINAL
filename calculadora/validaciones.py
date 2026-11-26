# Usamos re para validar el formato de la sección
import re
# Usamos math para asegurarnos que no metan valores infinitos o NaN con math.isfinite()
import math
# Para ir guardando los avisos (WARNING) cuando alguien escribe algo mal
import logs.logs


patron_seccion = r"^\s*([+-]?\d+(?:[.,]\d+)?)(?:\s*mm[2\u00b2])?\s*$"

def validar_numero_positivo(valor, variable):

    # Lo pasamos a texto por si acaso y le quitamos los espacios en blanco si tiene y pasamos a minusculas porsia
    texto_limpio = str(valor).strip().lower()

    # Si no se scribio nada, avisamos en el log y lanzamos error
    if texto_limpio == "":
        # Guardamos la advertencia en el archivo de logs indicando qué valor falló
        logs.logs.registrar_warning(
            "validaciones.validar_numero_positivo",
            f"Valor vacío ingresado en: {variable}"
        )
        raise ValueError(f"El valor a ingresar no puede estar vacío.")

    # Cambiamos la coma por punto por si escriben decimales con coma
    texto_normal = texto_limpio.replace(",", ".")

    # Intentamos pasarlo a decimal (si tiene letras, falla aqui)
    try:
        numero = float(texto_normal)
    except ValueError:
        logs.logs.registrar_warning(
            "validaciones.validar_numero_positivo",
            f"Formato no numérico ({valor}) en: {variable}"
        )
        raise ValueError(f"El valor ({variable}) debe ser un número válido.")

    # Verificamos que no sea NaN ni infinito
    if not math.isfinite(numero):
        logs.logs.registrar_warning(
            "validaciones.validar_numero_positivo",
            f"Valor no finito ({valor}) en: {variable}"
        )
        raise ValueError(f"El valor ({variable}) debe ser un número finito.")

    # No aceptamos cero ni números negativos
    if numero <= 0:
        logs.logs.registrar_warning(
            "validaciones.validar_numero_positivo",
            f"Valor menor o igual a cero ({numero}) en: {variable}"
        )
        raise ValueError(f"El valor ({variable}) debe ser mayor que cero.")

    return numero


def validar_seccion_transversal(seccion):
    # Quitamos espacios y pasamos todo a minúsculas porsia
    texto_limpio = str(seccion).strip().lower()

    if texto_limpio == "":
        logs.logs.registrar_warning(
            "validaciones.validar_seccion_transversal",
            "Sección transversal vacía"
        )
        raise ValueError("La sección transversal (A) no puede estar vacía.")

    # Comparamos lo que escribió el usuario con nuestro patrón regex
    coincidencia = re.match(patron_seccion, texto_limpio)

     # Si no encaja (escribió algo raro o con letras malas)
    if not coincidencia:
    # Anotamos el aviso en el log para que quede registro
        logs.logs.registrar_warning(
        "validaciones.validar_seccion_transversal",
        f"Formato de sección no admitido: ({seccion})'"
        )
        # Frenamos todo y le mostramos en pantalla cómo debe escribirlo
        raise ValueError(
            "Formato de sección inválido. Ejemplos admitidos: 2.5, 2,5, 2.5 mm2 o 2,5 mm²."
            )

    # Sacamos solo el número (sin el 'mm2') usando el primer paréntesis del patrón
    parte_numerica = coincidencia.group(1)

    return validar_numero_positivo(parte_numerica, "Sección transversal (A)")


# Revisa todos los datos juntos antes de hacer cualquier cálculo en el circuito
def validar_todas_las_entradas(voltaje, longitud, seccion, resistividad):
    # Validamos uno por uno; si alguno está mal, la función lanza ValueError y frena todo
    voltaje = validar_numero_positivo(voltaje, "Voltaje (V)")
    longitud = validar_numero_positivo(longitud, "Longitud (L)")
    seccion = validar_seccion_transversal(seccion)
    resistividad = validar_numero_positivo(resistividad, "Resistividad (p)")

    # Si los 4 estan bien, los devolvemos ya convertidos decimal
    return {
        "voltaje": voltaje,
        "longitud": longitud,
        "seccion": seccion,
        "resistividad": resistividad
    }



