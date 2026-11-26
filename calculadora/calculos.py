# De la carpeta calcuuladora importams el modulo materiales para los datos
import calculadora.materiales
import logs.logs
from utilidades.decoradores import auditar_operacion

def convertir_area_mm_m(mm2):
    # Formula : A(m**2) = A(mm**2) * 10e-6
    A_m2 = mm2 * 1e-6
    return A_m2


def calcular_longitud_total(longitud_inicial):

    # Multiplica la distancia por 2 para contar tanto la ida como la vuelta del cable
    L_total = 2 * longitud_inicial
    return L_total

@auditar_operacion("Cálculo completo del circuito DC")
def calcular_circuito(voltaje, resistencia_carga, material, longitud_inicial, mm2, id_calculo="0001"):

    # Obtenemos la resistividad en ohm por metro desde el módulo materiales
    resistividad = calculadora.materiales.obtener_resistividad(material)

    # Pasamos el área a metros cuadrados
    A_m2 = convertir_area_mm_m(mm2)

    # Sacamos la longitud total (ida y vuelta)
    L_total = calcular_longitud_total(longitud_inicial)

    # Calculamos la resistencia del cable
    Rc = (resistividad * L_total) / A_m2

    # Sumamos la resistencia de la carga ingresada en streamlit más la del cable
    Rt = resistencia_carga + Rc

    # Aplicamos la Ley de Ohm para sacar la corriente
    I = voltaje / Rt

    # Calculamos cuánta tensión tiene el cable
    Vc = I * Rc

    # Calculamos la potencia que se disipa en el cable
    Pc = (I ** 2) * Rc

    # Guardamos en el log que el calculo salió bien
    logs.logs.registrar_info(
        "calculadora.calculos",
        f"cálculo completado "
    )

    # Devolvemos todo redondeado a 4 decimales 
    resultados = {
        "Rc": round(Rc, 4),
        "Rt": round(Rt, 4),
        "I": round(I, 4),
        "Vc": round(Vc, 4),
        "Pc": round(Pc, 4)
    }

    return resultados