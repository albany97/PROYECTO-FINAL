# Diccionario con resistividades de referencia a 20 grados en ohm por metro

materiales_resistividad = {
    "Cobre": 1.68e-8,
    "Aluminio": 2.65e-8,
    "Plata": 1.59e-8,
    "Oro": 2.21e-8,
    "Hierro": 8.90e-8
}


def obtener_lista_materiales():
    # Devuelve los nombres de los materiales disponibles para el selector de Streamlit
    #keys es para obtener todas las claves de los diccionarios
    return list(materiales_resistividad.keys())


def obtener_resistividad(material):
    # Verifica que el material exista en el diccionario; si no, lanza error
    if material not in materiales_resistividad:
        raise ValueError(f"Material '{material}' no encontrado")
    return materiales_resistividad[material]