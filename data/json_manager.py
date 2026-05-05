"""
json_manager.py — Capa de persistencia: lectura y escritura del archivo config.json.

Librería `json`: Serialización/deserialización de datos Python ↔ formato JSON.
Librería `os`: Verificación de existencia de archivos en el sistema de archivos.
Librería `typing`: Anotaciones de tipos para mayor claridad y seguridad en el código.
"""

import json                          # Manejo de archivos JSON
import os                            # Operaciones del sistema de archivos
from typing import Any, Dict, List   # Tipos para anotaciones estrictas
from data.logger import logger       # Logger global del sistema


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPCIONES PERSONALIZADAS
# Principio: Encapsulación de errores — cada tipo de fallo tiene su propia clase.
# ─────────────────────────────────────────────────────────────────────────────

class ErrorLecturaDatos(Exception):
    """Se lanza cuando no se puede leer el archivo de persistencia."""
    pass


class ErrorEscrituraDatos(Exception):
    """Se lanza cuando no se puede escribir en el archivo de persistencia."""
    pass


class ErrorDatosCorruptos(Exception):
    """Se lanza cuando el JSON existe pero su estructura es inválida."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# ESTRUCTURA VACÍA POR DEFECTO
# Garantiza que el archivo JSON siempre tenga las claves necesarias.
# ─────────────────────────────────────────────────────────────────────────────

ESTRUCTURA_INICIAL: Dict[str, List] = {
    "clientes": [],      # Lista de objetos cliente serializados
    "servicios": [],     # Lista de objetos servicio serializados
    "reservas": [],      # Lista de objetos reserva serializados
    "usuarios": []       # Lista de objetos usuario serializados (para login)

}


class GestorJSON:
    """
    Clase responsable de toda la interacción con el archivo JSON.

    Principio de diseño: Responsabilidad Única (SRP) — esta clase SOLO
    lee y escribe datos; no sabe nada de clientes, servicios ni reservas.
    """

    def __init__(self, ruta_archivo: str = "config.json") -> None:
        """
        Inicializa el gestor con la ruta del archivo de persistencia.

        Args:
            ruta_archivo (str): Ruta al archivo config.json.
        """
        self._ruta: str = ruta_archivo          # Ruta encapsulada (privada)
        self._inicializar_archivo()             # Crear el archivo si no existe

    def _inicializar_archivo(self) -> None:
        """
        Crea el archivo JSON con estructura vacía si no existe.
        Método privado (prefijo _): solo para uso interno de la clase.
        """
        if not os.path.exists(self._ruta):
            logger.info(f"Archivo '{self._ruta}' no encontrado. Creando estructura inicial...")
            self._escribir(ESTRUCTURA_INICIAL)
            logger.info("Archivo de persistencia creado exitosamente.")

    def leer(self) -> Dict[str, Any]:
        """
        Lee y retorna todos los datos del archivo JSON.

        Returns:
            Dict[str, Any]: Diccionario con claves 'clientes', 'servicios', 'reservas'.

        Raises:
            ErrorLecturaDatos: Si el archivo no se puede abrir.
            ErrorDatosCorruptos: Si el contenido no es JSON válido.
        """
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                datos: Dict[str, Any] = json.load(archivo)

            # Validar que el JSON tenga las claves esperadas
            for clave in ESTRUCTURA_INICIAL:
                if clave not in datos:
                    logger.warning(f"Clave '{clave}' faltante en JSON. Añadiendo vacía.")
                    datos[clave] = []

            logger.debug("Datos leídos correctamente desde el archivo de persistencia.")
            return datos

        except json.JSONDecodeError as e:
            # El archivo existe pero no es JSON válido
            mensaje = f"El archivo '{self._ruta}' contiene JSON inválido: {e}"
            logger.error(mensaje)
            raise ErrorDatosCorruptos(mensaje) from e

        except OSError as e:
            # Error de permisos, disco lleno, etc.
            mensaje = f"No se pudo leer '{self._ruta}': {e}"
            logger.error(mensaje)
            raise ErrorLecturaDatos(mensaje) from e

    def _escribir(self, datos: Dict[str, Any]) -> None:
        """
        Escribe el diccionario completo en el archivo JSON (sobreescribe).

        Args:
            datos (Dict[str, Any]): Datos completos a persistir.

        Raises:
            ErrorEscrituraDatos: Si el archivo no se puede escribir.
        """
        try:
            with open(self._ruta, "w", encoding="utf-8") as archivo:
                # indent=4 para formato legible por humanos
                json.dump(datos, archivo, ensure_ascii=False, indent=4)
            logger.debug("Datos escritos correctamente en el archivo de persistencia.")

        except OSError as e:
            mensaje = f"No se pudo escribir en '{self._ruta}': {e}"
            logger.error(mensaje)
            raise ErrorEscrituraDatos(mensaje) from e

    def guardar_sección(self, clave: str, lista: List[Dict]) -> None:
        """
        Actualiza una sección específica del JSON ('clientes', 'servicios' o 'reservas').

        Args:
            clave (str): Nombre de la sección a actualizar.
            lista (List[Dict]): Nueva lista de objetos serializados.

        Raises:
            ValueError: Si la clave no es una sección válida.
        """
        if clave not in ESTRUCTURA_INICIAL:
            raise ValueError(f"Sección '{clave}' no válida. Use: {list(ESTRUCTURA_INICIAL.keys())}")

        datos = self.leer()           # Cargar estado actual completo
        datos[clave] = lista          # Reemplazar solo la sección indicada
        self._escribir(datos)         # Persistir todo de vuelta
        logger.info(f"Sección '{clave}' actualizada con {len(lista)} elemento(s).")
