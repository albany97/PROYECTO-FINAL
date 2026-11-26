
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
# importar LOGS !!!

# LOGS

# Ruta relativa estándar a la raíz del proyecto
RUTA_CARPETA_DATA = Path("data")
RUTA_ARCHIVO_HISTORIAL = RUTA_CARPETA_DATA / "historial.json"

#Crear carpetas o validar que ya esten hechas
def inicializar_historial() -> None:

    try:
        RUTA_CARPETA_DATA.mkdir(parents = True, exist_ok = True)

        if not RUTA_ARCHIVO_HISTORIAL.exists():
            
            with open(RUTA_ARCHIVO_HISTORIAL, mode = "w", encoding = "utf-8") as archivo:
                json.dump([], archivo, indent = 2, ensure_ascii = False) #ensure_ascii -> Para leer bien el archivo
            
            #LOGS

    except Exception as error:
        #LOGS
        
        raise error


#Carga todos los calculos almacenados al data/historial.json
#Tmb abarca lo del manejo de excepciones sin detener la app
def cargar_historial() -> List[Dict[str, Any]]: #Lista de registros de cálculos guardados

    inicializar_historial() #La primera q creamos

    try:
        with open(RUTA_ARCHIVO_HISTORIAL, mode = "r", encoding = "utf-8") as archivo:
            contenido = archivo.read().strip()

            if not contenido:
                # El archivo existe pero está vacío
                #LOGS

                with open(RUTA_ARCHIVO_HISTORIAL, mode = "w", encoding = "utf-8") as salida:

                    json.dump([], salida, indent = 2)
                
                return []

            datos = json.loads(contenido)
            
            if not isinstance(datos, list):
                #LOGS
                _respaldar_archivo_danado()

                return []

            #LOGS

            return datos

    except json.JSONDecodeError as json_error:
        #LOGS

        _respaldar_archivo_danado()
        return []
    
    except Exception as error:

        # LOGS

        return []


#Registros de calculos exitosos nuevos en el archivo data/historial.json
#El registro va asi:
# ID: Identificador secuencial (formato: 0000)
# Fecha y hora: Usando timestamp ISO
# Entradas: Diccionario con parámetros ingresados por el usuario
# Resultados: Diccionario con magnitudes eléctricas calculadas
def guardar_calculo(entradas: Dict[str, Any], resultados: Dict[str, Any]) -> Dict[str, Any]:

    historial_actual = cargar_historial()

    # Generación de ID incrementando
    siguiente_numero = len(historial_actual) + 1
    nuevo_id = f"{siguiente_numero:04d}" #El :04d es para que cumpla el formato de 000X 

    ahora_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S") #Parecido al anterior, se usa para convertir de datetime a texto, y los % para poder mostrar bien ese texto

    registro = {
        "id": nuevo_id,
        "fecha_hora": ahora_str,
        "entradas": entradas,
        "resultados": resultados,
    }

    historial_actual.append(registro)

    try:
        with open(RUTA_ARCHIVO_HISTORIAL, mode = "w", encoding = "utf-8") as archivo:

            json.dump(historial_actual, archivo, indent = 2, ensure_ascii = False)

        # LOGS

        return registro
    
    except Exception as error:
        # LOGS

        raise error


# Para vaciar el historial y reestablecer una lista completamente vacia
# Use bool para q regrese true si se hizo, o false si no se hizo
def limpiar_historial() -> bool:

    try:
        with open(RUTA_ARCHIVO_HISTORIAL, mode = "w", encoding = "utf-8") as archivo:

            json.dump([], archivo, indent=2, ensure_ascii=False)

        # LOGS

        return True
    
    except Exception as error:

        # LOGS

        return False

# En caso de json dañadito
# Hace copia del respaldo y reinicia el archivo (o algo asi)
def _respaldar_archivo_danado() -> None:

    try:
        # Para marcar la parte del respaldo y asi
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_respaldo = RUTA_CARPETA_DATA / f"historial_corrupto_{timestamp}.bak"

        if RUTA_ARCHIVO_HISTORIAL.exists():

            RUTA_ARCHIVO_HISTORIAL.rename(ruta_respaldo)

            # LOGS

        with open(RUTA_ARCHIVO_HISTORIAL, mode = "w", encoding = "utf-8") as archivo:

            json.dump([], archivo, indent = 2)

    except Exception as error:
        # LOGS
        """basta"""