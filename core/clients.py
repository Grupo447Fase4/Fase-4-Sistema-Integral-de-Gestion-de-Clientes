"""
clients.py — Implementación concreta de los tipos de cliente.

Principios aplicados:
- HERENCIA: Cada clase hereda de ClienteBase.
- POLIMORFISMO: Las propiedades `rol` y `descuento` se comportan distinto
  en cada subclase, aunque se llamen igual.
- ENCAPSULACIÓN: Atributos privados con acceso vía properties.
"""

from typing import Dict, Any                        # Tipado fuerte
from core.base_models import ClienteBase            # Clase abstracta padre
from data.logger import logger                      # Sistema de logs


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE CORRIENTE
# El cliente más básico, sin beneficios adicionales.
# ─────────────────────────────────────────────────────────────────────────────

class ClienteCorriente(ClienteBase):
    """
    Cliente estándar sin beneficios especiales ni descuentos.
    Primer nivel del sistema de roles.
    """

    def __init__(self, nombre: str, email: str, telefono: str) -> None:
        """
        Crea un cliente de tipo corriente.

        Args:
            nombre (str): Nombre completo.
            email (str): Correo electrónico.
            telefono (str): Número de contacto.
        """
        super().__init__(nombre, email, telefono)
        logger.info(f"Cliente corriente creado: {nombre} ({email})")

    # ── Implementación de los métodos abstractos obligatorios ──

    @property
    def rol(self) -> str:
        """Polimorfismo: retorna el rol específico de esta subclase."""
        return "corriente"

    @property
    def descuento(self) -> float:
        """Sin descuento para cliente corriente."""
        return 0.0   # 0%

    def descripcion(self) -> str:
        """Descripción legible del cliente."""
        return (f"[CORRIENTE] {self._nombre} | "
                f"Email: {self._email} | Tel: {self._telefono}")

    def validar(self) -> bool:
        """Valida que el cliente tiene los datos mínimos necesarios."""
        return bool(self._nombre and self._email and self._telefono)

    # ── Serialización: convierte objeto → diccionario para guardar en JSON ──

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializa el cliente a un diccionario compatible con JSON.

        Returns:
            Dict[str, Any]: Datos del cliente en formato persistible.
        """
        return {
            "id": self._id,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "rol": self.rol,
            "descuento": self.descuento,
            "activo": self._activo,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "ClienteCorriente":
        """
        Reconstruye un ClienteCorriente desde un diccionario cargado del JSON.

        Args:
            datos (Dict[str, Any]): Diccionario con los campos del cliente.

        Returns:
            ClienteCorriente: Instancia reconstruida.
        """
        instancia = cls(
            nombre=datos["nombre"],
            email=datos["email"],
            telefono=datos["telefono"]
        )
        # Restaurar campos que no pasan por el constructor
        instancia._id = datos["id"]
        instancia._activo = datos.get("activo", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE REGULAR
# Cliente con historial, recibe un descuento del 10%.
# ─────────────────────────────────────────────────────────────────────────────

class ClienteRegular(ClienteBase):
    """
    Cliente habitual que ya ha usado los servicios con frecuencia.
    Segundo nivel del sistema de roles. Recibe 10% de descuento.
    """

    # Constante de clase: el descuento no cambia para todos los regulares
    _DESCUENTO_REGULAR: float = 0.10   # 10%

    def __init__(self, nombre: str, email: str, telefono: str,
                 reservas_realizadas: int = 0) -> None:
        """
        Crea un cliente regular.

        Args:
            nombre (str): Nombre completo.
            email (str): Correo electrónico.
            telefono (str): Número de contacto.
            reservas_realizadas (int): Historial de reservas previas.
        """
        super().__init__(nombre, email, telefono)

        # Validación de tipo fuerte para el entero
        if not isinstance(reservas_realizadas, int) or reservas_realizadas < 0:
            raise ValueError("reservas_realizadas debe ser un entero no negativo.")

        self._reservas_realizadas: int = reservas_realizadas
        logger.info(f"Cliente regular creado: {nombre} | Reservas previas: {reservas_realizadas}")

    @property
    def rol(self) -> str:
        return "regular"

    @property
    def descuento(self) -> float:
        return self._DESCUENTO_REGULAR

    @property
    def reservas_realizadas(self) -> int:
        return self._reservas_realizadas

    def incrementar_reservas(self) -> None:
        """Incrementa el contador de reservas históricas del cliente."""
        self._reservas_realizadas += 1

    def descripcion(self) -> str:
        return (f"[REGULAR] {self._nombre} | "
                f"Email: {self._email} | "
                f"Descuento: {int(self._DESCUENTO_REGULAR * 100)}% | "
                f"Reservas: {self._reservas_realizadas}")

    def validar(self) -> bool:
        return bool(self._nombre and self._email and self._telefono)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "rol": self.rol,
            "descuento": self.descuento,
            "reservas_realizadas": self._reservas_realizadas,
            "activo": self._activo,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "ClienteRegular":
        instancia = cls(
            nombre=datos["nombre"],
            email=datos["email"],
            telefono=datos["telefono"],
            reservas_realizadas=datos.get("reservas_realizadas", 0)
        )
        instancia._id = datos["id"]
        instancia._activo = datos.get("activo", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# CLIENTE VIP
# El nivel más alto, con mayores descuentos y servicios prioritarios.
# ─────────────────────────────────────────────────────────────────────────────

class ClienteVIP(ClienteBase):
    """
    Cliente de alto valor con acceso prioritario y 25% de descuento.
    Tercer nivel del sistema de roles (el más alto).
    """

    _DESCUENTO_VIP: float = 0.25   # 25% de descuento

    def __init__(self, nombre: str, email: str, telefono: str,
                 empresa: str = "", credito_disponible: float = 0.0) -> None:
        """
        Crea un cliente VIP.

        Args:
            nombre (str): Nombre completo.
            email (str): Correo electrónico.
            telefono (str): Número de contacto.
            empresa (str): Nombre de la empresa que representa (opcional).
            credito_disponible (float): Crédito en sistema para usar en reservas.
        """
        super().__init__(nombre, email, telefono)

        if not isinstance(credito_disponible, (int, float)) or credito_disponible < 0:
            raise ValueError("El crédito disponible debe ser un número no negativo.")

        self._empresa: str = empresa.strip()
        self._credito_disponible: float = float(credito_disponible)
        logger.info(f"Cliente VIP creado: {nombre} | Empresa: {empresa or 'N/A'}")

    @property
    def rol(self) -> str:
        return "vip"

    @property
    def descuento(self) -> float:
        return self._DESCUENTO_VIP

    @property
    def empresa(self) -> str:
        return self._empresa

    @property
    def credito_disponible(self) -> float:
        return self._credito_disponible

    @credito_disponible.setter
    def credito_disponible(self, valor: float) -> None:
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("El crédito debe ser un número no negativo.")
        self._credito_disponible = float(valor)

    def descripcion(self) -> str:
        return (f"[VIP ★] {self._nombre} | "
                f"Empresa: {self._empresa or 'N/A'} | "
                f"Descuento: {int(self._DESCUENTO_VIP * 100)}% | "
                f"Crédito: ${self._credito_disponible:,.2f}")

    def validar(self) -> bool:
        return bool(self._nombre and self._email and self._telefono)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "email": self._email,
            "telefono": self._telefono,
            "rol": self.rol,
            "descuento": self.descuento,
            "empresa": self._empresa,
            "credito_disponible": self._credito_disponible,
            "activo": self._activo,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "ClienteVIP":
        instancia = cls(
            nombre=datos["nombre"],
            email=datos["email"],
            telefono=datos["telefono"],
            empresa=datos.get("empresa", ""),
            credito_disponible=datos.get("credito_disponible", 0.0)
        )
        instancia._id = datos["id"]
        instancia._activo = datos.get("activo", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# FÁBRICA DE CLIENTES
# Función utilitaria para reconstruir clientes del JSON sin conocer su rol.
# Principio: Abstracción — el llamador no necesita saber qué clase instanciar.
# ─────────────────────────────────────────────────────────────────────────────

def cliente_desde_dict(datos: Dict[str, Any]) -> ClienteBase:
    """
    Reconstruye el objeto cliente correcto según el campo 'rol' del diccionario.

    Args:
        datos (Dict[str, Any]): Diccionario cargado desde JSON.

    Returns:
        ClienteBase: Instancia del tipo concreto correspondiente.

    Raises:
        ValueError: Si el rol no es reconocido.
    """
    rol: str = datos.get("rol", "").lower()

    # Mapa de roles → clases concretas (Polimorfismo en acción)
    fabricas = {
        "corriente": ClienteCorriente,
        "regular": ClienteRegular,
        "vip": ClienteVIP
    }

    if rol not in fabricas:
        raise ValueError(f"Rol de cliente desconocido: '{rol}'")

    return fabricas[rol].from_dict(datos)
