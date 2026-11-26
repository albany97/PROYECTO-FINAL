"""
Módulo de Decoradores Personalizados
====================================
Contiene decoradores reutilizables diseñados para enriquecer el comportamiento
de funciones clave del proyecto sin alterar su lógica interna.

Tema de Programación I:
Un decorador es una función que recibe otra función como parámetro, agrega
funcionalidades previas o posteriores a su ejecución (como medición de tiempo o
registro en bitácora) y retorna la función modificada (función de orden superior).
"""

import functools
import time
from typing import Any, Callable
from logs.logs import registrar_error, registrar_info


def auditar_operacion(nombre_operacion: str = "") -> Callable:
    """
    Decorador que mide el tiempo de ejecución de una función y registra automáticamente
    en 'logs/app.log' su inicio, resultado exitoso o error, y duración en milisegundos.

    Uso didáctico:
        @auditar_operacion("Cálculo completo del circuito DC")
        def calcular_circuito_completo(...):
            ...

    Args:
        nombre_operacion (str, opcional): Etiqueta descriptiva para el log. Si no se
                                         especifica, se utiliza el nombre de la función.

    Returns:
        Callable: Función decorada.
    """
    def decorador(funcion: Callable) -> Callable:
        @functools.wraps(funcion)
        def envoltura(*args: Any, **kwargs: Any) -> Any:
            nombre = nombre_operacion if nombre_operacion else funcion.__name__
            origen = f"utilidades.decoradores.{nombre}"
            inicio = time.perf_counter()
            registrar_info(origen, f"Iniciando operación: '{nombre}'")

            try:
                resultado = funcion(*args, **kwargs)
                duracion_ms = (time.perf_counter() - inicio) * 1000.0
                registrar_info(
                    origen,
                    f"Operación '{nombre}' completada con éxito | duración={duracion_ms:.2f} ms"
                )
                return resultado
            except Exception as error:
                duracion_ms = (time.perf_counter() - inicio) * 1000.0
                registrar_error(
                    origen,
                    f"Fallo en operación '{nombre}' | error={type(error).__name__}: {error} | "
                    f"duración={duracion_ms:.2f} ms"
                )
                # Re-lanzar la excepción para no enmascarar errores de la aplicación
                raise

        return envoltura
    return decorador
