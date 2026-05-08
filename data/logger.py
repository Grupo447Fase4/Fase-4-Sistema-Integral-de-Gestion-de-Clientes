"""
logger.py — Módulo de configuración del sistema de logging.

Librería `logging`: Módulo estándar de Python para registrar eventos,
advertencias y errores en archivos o consola de forma estructurada.

Librería `os`: Permite interactuar con el sistema de archivos
(crear rutas, verificar existencia de directorios, etc.).
"""

import logging  # Módulo estándar para registrar eventos del sistema
import os       # Módulo para manejo de rutas y sistema de archivos


def configurar_logger(nombre: str = "SoftwareFJ", archivo_log: str = "app.log") -> logging.Logger:
    """
    Configura y retorna un logger con salida a archivo y consola.

    Args:
        nombre (str): Nombre identificador del logger (aparece en cada línea del log).
        archivo_log (str): Ruta del archivo donde se guardarán los registros.

    Returns:
        logging.Logger: Instancia del logger lista para usar.
    """

    # Obtener (o crear) una instancia de logger con el nombre dado.
    # Si ya existe un logger con ese nombre, Python lo reutiliza.
    logger = logging.getLogger(nombre)

    # Establecer el nivel mínimo de severidad que se registrará.
    # DEBUG < INFO < WARNING < ERROR < CRITICAL
    logger.setLevel(logging.DEBUG)

    # Evitar agregar manejadores duplicados si la función se llama varias veces
    if logger.handlers:
        return logger

    # ──────────────────────────────────────────────
    # Formato de cada línea del log:
    # [2024-01-15 10:30:00] [NIVEL   ] Mensaje del evento
    # ──────────────────────────────────────────────
    formato = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # ── Manejador de ARCHIVO: guarda todos los logs en disco ──
    manejador_archivo = logging.FileHandler(archivo_log, encoding="utf-8")
    manejador_archivo.setLevel(logging.DEBUG)       # Captura todo desde DEBUG
    manejador_archivo.setFormatter(formato)         # Aplica el formato definido

    # ── Manejador de CONSOLA: muestra logs importantes en pantalla ──
    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.WARNING)     # Solo WARNING, ERROR y CRITICAL
    manejador_consola.setFormatter(formato)

    # Registrar ambos manejadores en el logger
    logger.addHandler(manejador_archivo)
    logger.addHandler(manejador_consola)

    return logger


# ── Instancia global del logger ──
# Se importa desde otros módulos con: from data.logger import logger
logger = configurar_logger()