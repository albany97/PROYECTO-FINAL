import logging

def configurar_registro():
    #logging.basicConfig() función del módulo logging que sirve para hacer una configuración rápida y básica del sistema de registros (logs)
    logging.basicConfig(
        #filename destino hacia donde iran los logs
        filename="logs/app.log",
        #level indica desde cual nivel se muestran los mensajes
        level=logging.INFO,
        #format estructura de cada linea registrada (fecha,hora,nivel,mensaje y asi)
        format="%(asctime)s | %(levelname)s | %(message)s",
        #dateftm formato de fecha y hora
        #año-mes-dia   hora:minutos:segundos
        #Usa los códigos estándar de time.strftime() (como %Y, %m, %d, %H, %M, %S).
        datefmt="%Y-%m-%d  |  %H:%M:%S",
        #encording codificacion del archivo
        #utf-8 permite tildes y caracteres especiales
        encoding="utf-8",
        #force cierra los handlers anteriores y aplica la nueva confi de una
        force=True
    )

def registrar_info(modulo, mensaje):
    configurar_registro()
    logging.info(f"{modulo} | {mensaje}")
    
    
def registrar_warning(modulo, mensaje):
    # Llama a la configuración y guarda una advertencia que no detiene el programa (nivel WARNING)
    configurar_registro()
    logging.warning(f"{modulo} | {mensaje}")
    
    
def registrar_error(modulo, mensaje):
    # Llama a la configuración y guarda un fallo capturado por excepción (nivel ERROR)
    configurar_registro()
    logging.error(f"{modulo} | {mensaje}")



