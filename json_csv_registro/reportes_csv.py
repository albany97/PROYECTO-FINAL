
import csv
import io
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from logs.logs import registrar_error, registrar_info, registrar_warning


RUTA_CARPETA_REPORTES = Path("reportes")

encabezados_CSV: List[str] = [
    "id",
    "fecha_hora",
    "tension_V",
    "resistencia_carga_ohm",
    "material",
    "resistividad_ohm_m",
    "longitud_ida_m",
    "seccion_mm2",
    "longitud_total_m",
    "resistencia_cable_ohm",
    "resistencia_total_ohm",
    "corriente_A",
    "caida_tension_cable_V",
    "potencia_disipada_cable_W",
]


def aplanar_registro(registro: Dict) -> Dict[str, str]:
    """
    Convierte la estructura anidada de un registro de cálculo en un diccionario plano
    con las columnas correspondientes al encabezado CSV.

    Args:
        registro (Dict): Registro del historial con claves 'entradas' y 'resultados'.

    Returns:
        Dict[str, str]: Diccionario plano listo para DictWriter de csv.
    """
    entradas = registro.get("entradas", {})
    resultados = registro.get("resultados", {})

    longitud_ida = float(entradas.get("longitud_ida_m", 0) or 0)
    longitud_total = float(resultados.get("longitud_total_m", longitud_ida * 2) or 0)

    rc = float(resultados.get("resistencia_cable_ohm", resultados.get("Rc", 0)) or 0)
    rt = float(resultados.get("resistencia_total_ohm", resultados.get("Rt", 0)) or 0)
    corriente = float(resultados.get("corriente_A", resultados.get("I", 0)) or 0)
    vc = float(resultados.get("caida_tension_cable_V", resultados.get("Vc", 0)) or 0)
    pc = float(resultados.get("potencia_disipada_cable_W", resultados.get("Pc", 0)) or 0)

    return {
        "id": str(registro.get("id", "")),
        "fecha_hora": str(registro.get("fecha_hora", "")),
        "tension_V": f"{float(entradas.get('tension_V', 0) or 0):.4f}",
        "resistencia_carga_ohm": f"{float(entradas.get('resistencia_carga_ohm', 0) or 0):.4f}",
        "material": str(entradas.get("material", "")),
        "resistividad_ohm_m": f"{float(entradas.get('resistividad_ohm_m', 0) or 0):.4e}",
        "longitud_ida_m": f"{longitud_ida:.4f}",
        "seccion_mm2": f"{float(entradas.get('seccion_mm2', 0) or 0):.4f}",
        "longitud_total_m": f"{longitud_total:.4f}",
        "resistencia_cable_ohm": f"{rc:.6f}",
        "resistencia_total_ohm": f"{rt:.6f}",
        "corriente_A": f"{corriente:.6f}",
        "caida_tension_cable_V": f"{vc:.6f}",
        "potencia_disipada_cable_W": f"{pc:.6f}",
    }
    



def generar_csv_en_memoria(registros: Iterable[Dict]) -> str:

    buffer_salida = io.StringIO()
    escritor = csv.DictWriter(
        buffer_salida,
        fieldnames = encabezados_CSV,
        delimiter = ";",
        lineterminator = "\n"
    )

    escritor.writeheader()

    contador = 0
    for registro in registros:
        fila = aplanar_registro(registro)
        escritor.writerow(fila)
        contador += 1

    contenido = buffer_salida.getvalue()

    # LOGS
    if contador == 0:
        registrar_warning(
            "json_csv_registro.reportes_csv",
            "Generación de CSV en memoria completada sin registros coincidentes.",
        )
    else:
        registrar_info(
            "json_csv_registro.reportes_csv",
            f"Reporte CSV en memoria generado con {contador} registros.",
        )

    return contenido
def exportar_reporte_a_disco(
    registros: Iterable[Dict],
    nombre_prefijo: str = "reporte_calculos"
) -> Optional[Path]:

    try:
        RUTA_CARPETA_REPORTES.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_archivo = RUTA_CARPETA_REPORTES / f"{nombre_prefijo}_{timestamp}.csv"

        contenido_csv = generar_csv_en_memoria(registros)

        with open(ruta_archivo, mode="w", encoding="utf-8-sig", newline="") as f:
            f.write(contenido_csv)

        registrar_info(
            "json_csv_registro.reportes_csv",
            f"Reporte exportado exitosamente a archivo: '{ruta_archivo}'",
        )
        return ruta_archivo
    
    except Exception as error:
        registrar_error(
            "json_csv_registro.reportes_csv",
            f"Fallo al exportar reporte a disco: {type(error).__name__}: {error}",
        )
        return None