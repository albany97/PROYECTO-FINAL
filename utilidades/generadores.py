
from pathlib import Path
from typing import Dict, Generator, List, Optional, Union


def generar_registros_historial(
    registros: List[Dict],
    filtro_material: Optional[str] = None,
    filtro_fecha: Optional[str] = None
) -> Generator[Dict, None, None]:
    
    for registro in registros:
        entradas = registro.get("entradas", {})
        material_registro = entradas.get("material", "")
        fecha_registro = registro.get("fecha_hora", "")

        # Filtro de material (si está activo y no coincide, se omite)
        if filtro_material and filtro_material != "Todos":
            if material_registro.lower() != filtro_material.lower():
                continue

        # Filtro de fecha (si está activo y no coincide el prefijo YYYY-MM-DD, se omite)
        if filtro_fecha:
            if not fecha_registro.startswith(filtro_fecha):
                continue

        # Entrega el registro actual de forma diferida
        yield registro


def generar_lineas_log(
    ruta_archivo: Union[str, Path] = "logs/app.log",
    filtro_nivel: Optional[str] = None
) -> Generator[Dict[str, str], None, None]:

    ruta = Path(ruta_archivo)
    if not ruta.is_file():
        return

    nivel_busqueda = filtro_nivel.upper().strip() if filtro_nivel and filtro_nivel.upper() != "TODOS" else None

    # Apertura en modo lectura streaming con codificación segura
    with open(ruta, mode="r", encoding="utf-8", errors="replace") as archivo:
        for numero_linea, linea in enumerate(archivo, start=1):
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue

            # Separar los campos por el delimitador '|'
            partes = [p.strip() for p in linea_limpia.split("|")]
            if len(partes) >= 4:
                fecha_hora = partes[0]
                nivel = partes[1].upper()
                modulo_funcion = partes[2]
                mensaje = "|".join(partes[3:])  # Preserva separadores adicionales en el mensaje

                if nivel_busqueda and nivel != nivel_busqueda:
                    continue

                yield {
                    "linea_num": str(numero_linea),
                    "fecha_hora": fecha_hora,
                    "nivel": nivel,
                    "origen": modulo_funcion,
                    "mensaje": mensaje,
                    "raw": linea_limpia,
                }
            else:
                # Líneas que no sigan el formato exacto (ej. trazas multilínea)
                if not nivel_busqueda:
                    yield {
                        "linea_num": str(numero_linea),
                        "fecha_hora": "-",
                        "nivel": "TEXTO",
                        "origen": "-",
                        "mensaje": linea_limpia,
                        "raw": linea_limpia,
                    }
