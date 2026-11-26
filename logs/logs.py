# Módulo estándar de Python para registrar eventos técnicos de la aplicación
import logging

# Path nos ayuda a manejar rutas de carpetas y archivos de forma limpia y portable
from pathlib import Path

# Ruta relativa al proyecto donde se guardarán los eventos del sistema
ruta_log = Path("logs/app.log")

# Variable interna para guardar el logger ya configurado y no crearlo varias veces
_logger = None


def configurar_logger():
    # Indicamos que modificaremos la variable _logger definida fuera de la función
    global _logger

    # Si ya se configuro antes, devolvemos ese mismo logger directamente
    if _logger is not None:
        return _logger

    #.parent saca la carpeta que contiene ese archivo: es decir, la carpeta "logs".
    #.mkdir(...) significa make directory (crear carpeta).
    #parents=True crea la carpeta "logs" (y cualquier carpeta intermedia si faltara).
    #exist_ok=True evita que Python lance un error si la carpeta "logs" ya existe.

    ruta_log.parent.mkdir(parents=True, exist_ok=True)


    # getLogger("calculadora_dc") busca o crea un canal propio con ese nombre para los registros del proyecto.
    logger = logging.getLogger("calculadora_dc")

    # Definimos el nivel mínimo a registrar: INFO captura INFO, WARNING y ERROR
    logger.setLevel(logging.INFO)

    # Solo agregamos el manejador de archivo si aún no tiene ninguno (evita líneas duplicadas)
    if not logger.handlers:
        # Abrimos 'logs/app.log' en modo 'a' (append: agregar al final sin borrar lo anterior)
        # Usamos utf-8 para que no fallen tildes ni caracteres especiales
        handler = logging.FileHandler(ruta_log, mode="a", encoding="utf-8")

        # El "formatter" (formato) define cómo se ve cada línea (fecha y hora, nivel, texto).
        formato = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Asignamos el formato al manejador de archivo
        handler.setFormatter(formato)

        # Conectamos el manejador de archivo al logger
        logger.addHandler(handler)

        # Evita que los mensajes suban al logger principal y se dupliquen en consola
        logger.propagate = False

    # Guardamos el logger listo para reutilizarlo en futuras llamadas
    _logger = logger
    return _logger


def registrar_info(modulo_o_funcion: str, mensaje: str):
    # Obtenemos el logger configurado
    logger = configurar_logger()
    # Registramos un evento normal/exitoso (nivel INFO) incluyendo origen y detalle
    logger.info(f"{modulo_o_funcion} | {mensaje}")


def registrar_warning(modulo_o_funcion: str, mensaje: str):
    # Obtenemos el logger configurado
    logger = configurar_logger()
    # Registramos una advertencia que no detiene el programa, ej. dato inválido (nivel WARNING)
    logger.warning(f"{modulo_o_funcion} | {mensaje}")


def registrar_error(modulo_o_funcion: str, mensaje: str):
    # Obtenemos el logger configurado
    logger = configurar_logger()
    # Registramos un fallo o excepción importante (nivel ERROR)
    logger.error(f"{modulo_o_funcion} | {mensaje}")