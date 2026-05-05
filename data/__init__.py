"""
data/__init__.py — Paquete de persistencia de datos.

Expone las clases principales para que otros módulos puedan importar
con: from data import GestorJSON, logger
"""

from data.json_manager import GestorJSON, ErrorLecturaDatos, ErrorEscrituraDatos, ErrorDatosCorruptos
from data.logger import logger

__all__ = [
    "GestorJSON",
    "ErrorLecturaDatos",
    "ErrorEscrituraDatos",
    "ErrorDatosCorruptos",
    "logger"
]
