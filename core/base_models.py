"""
base_models.py — Clases abstractas y Mixins del sistema.

Librería `abc`: Abstract Base Classes — permite definir clases y métodos
abstractos que obligan a las subclases a implementar ciertos comportamientos.
Esto es el núcleo del principio de ABSTRACCIÓN en POO.

Librería `uuid`: Genera identificadores únicos universales (UUID4) para
evitar colisiones de IDs entre objetos del sistema.

Librería `datetime`: Manejo de fechas y horas para timestamps de creación.

Librería `typing`: Herramientas para tipado fuerte (Dict, Any, Optional).
"""

from abc import ABC, abstractmethod          # Abstracción: clases y métodos abstractos
from uuid import uuid4                       # Generador de IDs únicos
from datetime import datetime                # Fecha/hora del sistema
from typing import Dict, Any, Optional       # Tipos para anotaciones estrictas


# ─────────────────────────────────────────────────────────────────────────────
# MIXIN: SerializableMixin
# Un Mixin es una clase auxiliar que añade funcionalidad sin ser la clase base.
# Principio: REUTILIZACIÓN — cualquier clase puede heredarlo para ganar
# los métodos to_dict() y from_dict() sin duplicar código.
# ─────────────────────────────────────────────────────────────────────────────

class SerializableMixin:
    """
    Mixin que añade capacidad de serialización/deserialización a cualquier clase.
    Permite convertir objetos Python ↔ diccionarios JSON.
    """

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el objeto a un diccionario serializable en JSON.
        Las subclases DEBEN sobreescribir este método para incluir sus atributos.

        Returns:
            Dict[str, Any]: Representación del objeto como diccionario.
        """
        raise NotImplementedError("La subclase debe implementar to_dict()")

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "SerializableMixin":
        """
        Reconstruye un objeto desde un diccionario (proceso inverso a to_dict).

        Args:
            datos (Dict[str, Any]): Diccionario cargado desde JSON.

        Returns:
            SerializableMixin: Instancia reconstruida del objeto.
        """
        raise NotImplementedError("La subclase debe implementar from_dict()")


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA BASE: EntidadBase
# Toda entidad del sistema (Cliente, Servicio, Reserva) hereda de aquí.
# Principio: ABSTRACCIÓN — define el contrato que deben cumplir las subclases.
# ─────────────────────────────────────────────────────────────────────────────

class EntidadBase(ABC, SerializableMixin):
    """
    Clase abstracta raíz del sistema. Define estructura y comportamiento común
    para Clientes, Servicios y Reservas.

    Hereda de:
        ABC: Activa el mecanismo de métodos abstractos.
        SerializableMixin: Añade capacidad de serialización.
    """

    def __init__(self, nombre: str) -> None:
        """
        Constructor base que asigna ID único y timestamp de creación.

        Args:
            nombre (str): Nombre descriptivo de la entidad.

        Raises:
            TypeError: Si el nombre no es una cadena de texto.
            ValueError: Si el nombre está vacío o solo contiene espacios.
        """
        # ── Validación de tipo fuerte ──
        if not isinstance(nombre, str):
            raise TypeError(f"El nombre debe ser str, se recibió: {type(nombre).__name__}")
        if not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")

        # ── Atributos privados con tipado explícito ──
        self._id: str = str(uuid4())                        # ID único e inmutable
        self._nombre: str = nombre.strip()                  # Nombre limpio de espacios
        self._fecha_creacion: str = datetime.now().isoformat()  # Timestamp ISO 8601

    # ── Properties: encapsulación con acceso controlado ──

    @property
    def id(self) -> str:
        """Retorna el ID único de la entidad (solo lectura)."""
        return self._id

    @property
    def nombre(self) -> str:
        """Retorna el nombre de la entidad."""
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        """
        Permite modificar el nombre con validación.

        Args:
            valor (str): Nuevo nombre.

        Raises:
            TypeError: Si no es string.
            ValueError: Si está vacío.
        """
        if not isinstance(valor, str):
            raise TypeError(f"Nombre debe ser str, recibido: {type(valor).__name__}")
        if not valor.strip():
            raise ValueError("El nombre no puede estar vacío.")
        self._nombre = valor.strip()

    @property
    def fecha_creacion(self) -> str:
        """Retorna la fecha de creación en formato ISO 8601 (solo lectura)."""
        return self._fecha_creacion

    # ── Métodos abstractos: contrato obligatorio para subclases ──

    @abstractmethod
    def descripcion(self) -> str:
        """
        Retorna una descripción legible de la entidad.
        OBLIGATORIO implementar en cada subclase.
        """
        ...

    @abstractmethod
    def validar(self) -> bool:
        """
        Valida que la entidad tiene todos los datos necesarios.
        OBLIGATORIO implementar en cada subclase.
        """
        ...

    # ── Método especial: representación del objeto ──

    def __repr__(self) -> str:
        """Representación técnica del objeto, útil en logs y debugging."""
        return f"{self.__class__.__name__}(id='{self._id[:8]}...', nombre='{self._nombre}')"

    def __str__(self) -> str:
        """Representación legible del objeto para mostrar al usuario."""
        return self._nombre


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA: ClienteBase
# Define el contrato específico para todos los tipos de cliente.
# Principio: HERENCIA — extiende EntidadBase añadiendo atributos de cliente.
# ─────────────────────────────────────────────────────────────────────────────

class ClienteBase(EntidadBase):
    """
    Clase abstracta para clientes. Hereda de EntidadBase y añade
    atributos como email, teléfono y rol. Las subclases concretas son:
    ClienteCorriente, ClienteRegular, ClienteVIP.
    """

    def __init__(self, nombre: str, email: str, telefono: str) -> None:
        """
        Constructor del cliente base.

        Args:
            nombre (str): Nombre completo del cliente.
            email (str): Correo electrónico (debe contener '@').
            telefono (str): Número de teléfono.

        Raises:
            TypeError: Si algún parámetro no es string.
            ValueError: Si email no tiene formato básico válido.
        """
        super().__init__(nombre)   # Delegar inicialización base

        # Validación de email mínima (contiene '@' y '.')
        if not isinstance(email, str) or "@" not in email or "." not in email:
            raise ValueError(f"Email inválido: '{email}'")

        if not isinstance(telefono, str) or not telefono.strip():
            raise TypeError("El teléfono debe ser una cadena no vacía.")

        self._email: str = email.strip().lower()      # Normalizar a minúsculas
        self._telefono: str = telefono.strip()
        self._activo: bool = True                      # Por defecto activo

    # ── Properties del cliente ──

    @property
    def email(self) -> str:
        return self._email

    @property
    def telefono(self) -> str:
        return self._telefono

    @property
    def activo(self) -> bool:
        return self._activo

    @activo.setter
    def activo(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise TypeError("El campo 'activo' debe ser booleano.")
        self._activo = valor

    @property
    @abstractmethod
    def rol(self) -> str:
        """
        Retorna el rol del cliente: 'corriente', 'regular' o 'vip'.
        OBLIGATORIO en cada subclase concreta.
        """
        ...

    @property
    @abstractmethod
    def descuento(self) -> float:
        """
        Retorna el porcentaje de descuento aplicable al cliente (0.0 - 1.0).
        OBLIGATORIO en cada subclase concreta.
        """
        ...


# ─────────────────────────────────────────────────────────────────────────────
# CLASE ABSTRACTA: ServicioBase
# Contrato para todos los servicios ofrecidos por Software FJ.
# ─────────────────────────────────────────────────────────────────────────────

class ServicioBase(EntidadBase):
    """
    Clase abstracta para servicios. Los servicios concretos son:
    ReservaSala, AlquilerEquipo, AsesoriaEspecializada.
    """

    def __init__(self, nombre: str, precio_hora: float, descripcion_servicio: str) -> None:
        """
        Constructor del servicio base.

        Args:
            nombre (str): Nombre del servicio.
            precio_hora (float): Costo por hora del servicio.
            descripcion_servicio (str): Descripción detallada del servicio.

        Raises:
            TypeError: Si precio_hora no es numérico.
            ValueError: Si precio_hora es negativo o cero.
        """
        super().__init__(nombre)

        # Tipado fuerte: precio debe ser numérico positivo
        if not isinstance(precio_hora, (int, float)):
            raise TypeError(f"precio_hora debe ser numérico, recibido: {type(precio_hora).__name__}")
        if precio_hora <= 0:
            raise ValueError(f"El precio por hora debe ser positivo, recibido: {precio_hora}")

        self._precio_hora: float = float(precio_hora)
        self._descripcion_servicio: str = descripcion_servicio.strip()
        self._disponible: bool = True     # Disponibilidad del servicio

    @property
    def precio_hora(self) -> float:
        return self._precio_hora

    @property
    def descripcion_servicio(self) -> str:
        return self._descripcion_servicio

    @property
    def disponible(self) -> bool:
        return self._disponible

    @disponible.setter
    def disponible(self, valor: bool) -> None:
        if not isinstance(valor, bool):
            raise TypeError("El campo 'disponible' debe ser booleano.")
        self._disponible = valor

    @abstractmethod
    def calcular_costo(self, horas: float) -> float:
        """
        Calcula el costo total del servicio según las horas solicitadas.
        OBLIGATORIO en cada subclase.
        """
        ...

    @property
    @abstractmethod
    def tipo_servicio(self) -> str:
        """Retorna el tipo de servicio como cadena de texto."""
        ...
