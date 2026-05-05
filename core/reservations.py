"""
reservations.py — Gestión de reservas del sistema.

Una Reserva integra: Cliente + Servicio + Duración + Estado.
Permite confirmar o cancelar la reserva con registro en logs.

Estados posibles del ciclo de vida de una reserva:
  pendiente → confirmada
  pendiente → cancelada
  confirmada → cancelada
"""

from datetime import datetime                        # Fechas y timestamps
from typing import Dict, Any, Optional               # Tipado fuerte
from core.base_models import ClienteBase, ServicioBase   # Tipos abstractos
from core.clients import cliente_desde_dict          # Fábrica de clientes
from core.services import servicio_desde_dict        # Fábrica de servicios
from data.logger import logger                       # Sistema de logs
from uuid import uuid4                               # IDs únicos


# ─────────────────────────────────────────────────────────────────────────────
# EXCEPCIONES ESPECÍFICAS DE RESERVAS
# Encapsulación de errores: cada fallo tiene su nombre claro.
# ─────────────────────────────────────────────────────────────────────────────

class ErrorReservaInvalida(Exception):
    """Se lanza cuando los datos de la reserva no son válidos."""
    pass


class ErrorTransicionEstado(Exception):
    """Se lanza cuando se intenta un cambio de estado no permitido."""
    pass


# ─────────────────────────────────────────────────────────────────────────────
# CLASE RESERVA
# Entidad central que conecta cliente, servicio, duración y estado.
# ─────────────────────────────────────────────────────────────────────────────

class Reserva:
    """
    Representa una reserva de servicio realizada por un cliente.

    Ciclo de vida:
        Creación → Estado 'pendiente'
        confirmar() → Estado 'confirmada'
        cancelar()  → Estado 'cancelada'
    """

    # Estados válidos del sistema de reservas
    ESTADOS_VALIDOS = {"pendiente", "confirmada", "cancelada"}

    # Transiciones permitidas: desde cada estado, qué estados se pueden alcanzar
    TRANSICIONES_PERMITIDAS: Dict[str, set] = {
        "pendiente": {"confirmada", "cancelada"},
        "confirmada": {"cancelada"},
        "cancelada": set()   # Estado terminal: no permite más cambios
    }

    def __init__(self, cliente: ClienteBase, servicio: ServicioBase,
                 horas: float, fecha_reserva: str = "",
                 notas: str = "") -> None:
        """
        Crea una nueva reserva en estado 'pendiente'.

        Args:
            cliente (ClienteBase): Objeto cliente que realiza la reserva.
            servicio (ServicioBase): Objeto servicio solicitado.
            horas (float): Duración de la reserva en horas.
            fecha_reserva (str): Fecha/hora deseada (formato libre).
            notas (str): Observaciones adicionales.

        Raises:
            TypeError: Si cliente o servicio no son del tipo correcto.
            ErrorReservaInvalida: Si los datos no pasan la validación.
        """
        # ── Validación de tipos con isinstance (tipado fuerte) ──
        if not isinstance(cliente, ClienteBase):
            raise TypeError("El parámetro 'cliente' debe ser una instancia de ClienteBase.")
        if not isinstance(servicio, ServicioBase):
            raise TypeError("El parámetro 'servicio' debe ser una instancia de ServicioBase.")

        # ── Validación del negocio ──
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise ErrorReservaInvalida("La duración debe ser un número positivo de horas.")
        if not servicio.disponible:
            raise ErrorReservaInvalida(f"El servicio '{servicio.nombre}' no está disponible.")
        if not cliente.activo:
            raise ErrorReservaInvalida(f"El cliente '{cliente.nombre}' no está activo.")

        # ── Atributos privados de la reserva ──
        self._id: str = str(uuid4())
        self._cliente: ClienteBase = cliente
        self._servicio: ServicioBase = servicio
        self._horas: float = float(horas)
        self._estado: str = "pendiente"                  # Estado inicial
        self._fecha_reserva: str = fecha_reserva.strip() or datetime.now().isoformat()
        self._fecha_creacion: str = datetime.now().isoformat()
        self._fecha_modificacion: str = self._fecha_creacion
        self._notas: str = notas.strip()

        # ── Cálculo del costo con descuento del cliente ──
        costo_bruto: float = servicio.calcular_costo(horas)
        descuento: float = cliente.descuento               # 0.0, 0.10 o 0.25
        self._costo_bruto: float = costo_bruto
        self._descuento_aplicado: float = descuento
        self._costo_total: float = costo_bruto * (1 - descuento)

        logger.info(
            f"Reserva CREADA | ID: {self._id[:8]} | "
            f"Cliente: {cliente.nombre} ({cliente.rol}) | "
            f"Servicio: {servicio.nombre} | "
            f"Horas: {horas} | Costo: ${self._costo_total:,.0f}"
        )

    # ── Properties de solo lectura ──

    @property
    def id(self) -> str:
        return self._id

    @property
    def cliente(self) -> ClienteBase:
        return self._cliente

    @property
    def servicio(self) -> ServicioBase:
        return self._servicio

    @property
    def horas(self) -> float:
        return self._horas

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def fecha_reserva(self) -> str:
        return self._fecha_reserva

    @property
    def fecha_creacion(self) -> str:
        return self._fecha_creacion

    @property
    def costo_bruto(self) -> float:
        return self._costo_bruto

    @property
    def descuento_aplicado(self) -> float:
        return self._descuento_aplicado

    @property
    def costo_total(self) -> float:
        return self._costo_total

    @property
    def notas(self) -> str:
        return self._notas

    # ── Acciones sobre el estado de la reserva ──

    def _cambiar_estado(self, nuevo_estado: str, motivo: str = "") -> None:
        """
        Método interno para cambiar el estado con validación de transición.

        Args:
            nuevo_estado (str): Estado destino.
            motivo (str): Razón del cambio (para el log).

        Raises:
            ErrorTransicionEstado: Si la transición no está permitida.
        """
        estados_alcanzables = self.TRANSICIONES_PERMITIDAS[self._estado]

        if nuevo_estado not in estados_alcanzables:
            raise ErrorTransicionEstado(
                f"No se puede pasar de '{self._estado}' a '{nuevo_estado}'. "
                f"Desde '{self._estado}' solo se puede ir a: {estados_alcanzables or {'(ninguno)'}}."
            )

        estado_anterior = self._estado
        self._estado = nuevo_estado
        self._fecha_modificacion = datetime.now().isoformat()

        logger.info(
            f"Reserva {self._id[:8]} | Estado: {estado_anterior} → {nuevo_estado} | "
            f"Cliente: {self._cliente.nombre} | Motivo: {motivo or 'Sin especificar'}"
        )

    def confirmar(self, motivo: str = "Confirmación manual") -> None:
        """
        Confirma la reserva. Solo válido desde estado 'pendiente'.

        Args:
            motivo (str): Razón de la confirmación.

        Raises:
            ErrorTransicionEstado: Si el estado actual no permite confirmar.
        """
        self._cambiar_estado("confirmada", motivo)

    def cancelar(self, motivo: str = "Cancelación manual") -> None:
        """
        Cancela la reserva. Válido desde 'pendiente' o 'confirmada'.

        Args:
            motivo (str): Razón de la cancelación.

        Raises:
            ErrorTransicionEstado: Si la reserva ya está cancelada.
        """
        self._cambiar_estado("cancelada", motivo)

    def resumen(self) -> str:
        """
        Retorna un resumen legible de la reserva para mostrar en la UI.

        Returns:
            str: Texto formateado con todos los datos relevantes.
        """
        descuento_pct = int(self._descuento_aplicado * 100)
        return (
            f"{'─'*50}\n"
            f"  ID Reserva : {self._id[:16]}...\n"
            f"  Cliente    : {self._cliente.nombre} [{self._cliente.rol.upper()}]\n"
            f"  Servicio   : {self._servicio.nombre}\n"
            f"  Duración   : {self._horas} hora(s)\n"
            f"  Fecha      : {self._fecha_reserva}\n"
            f"  Costo base : ${self._costo_bruto:>12,.2f}\n"
            f"  Descuento  : {descuento_pct}%  (-${self._costo_bruto * self._descuento_aplicado:,.2f})\n"
            f"  TOTAL      : ${self._costo_total:>12,.2f}\n"
            f"  Estado     : {self._estado.upper()}\n"
            f"  Notas      : {self._notas or 'Sin notas'}\n"
            f"{'─'*50}"
        )

    def __repr__(self) -> str:
        return (f"Reserva(id='{self._id[:8]}', "
                f"cliente='{self._cliente.nombre}', "
                f"servicio='{self._servicio.nombre}', "
                f"estado='{self._estado}')")

    # ── Serialización para persistencia JSON ──

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la reserva a diccionario para guardar en JSON."""
        return {
            "id": self._id,
            "cliente": self._cliente.to_dict(),       # Objeto cliente serializado
            "servicio": self._servicio.to_dict(),     # Objeto servicio serializado
            "horas": self._horas,
            "estado": self._estado,
            "fecha_reserva": self._fecha_reserva,
            "fecha_creacion": self._fecha_creacion,
            "fecha_modificacion": self._fecha_modificacion,
            "costo_bruto": self._costo_bruto,
            "descuento_aplicado": self._descuento_aplicado,
            "costo_total": self._costo_total,
            "notas": self._notas
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "Reserva":
        """
        Reconstruye una Reserva desde un diccionario del JSON.

        Args:
            datos (Dict[str, Any]): Datos de la reserva serializados.

        Returns:
            Reserva: Objeto reconstruido con estado preservado.
        """
        # Reconstruir cliente y servicio usando sus fábricas
        cliente = cliente_desde_dict(datos["cliente"])
        servicio = servicio_desde_dict(datos["servicio"])

        # Crear objeto reserva (esto recalcularía costos, los sobreescribimos después)
        instancia = cls(
            cliente=cliente,
            servicio=servicio,
            horas=datos["horas"],
            fecha_reserva=datos.get("fecha_reserva", ""),
            notas=datos.get("notas", "")
        )

        # Restaurar campos calculados y de control desde el JSON (no recalcular)
        instancia._id = datos["id"]
        instancia._estado = datos.get("estado", "pendiente")
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        instancia._fecha_modificacion = datos.get("fecha_modificacion", instancia._fecha_modificacion)
        instancia._costo_bruto = datos.get("costo_bruto", instancia._costo_bruto)
        instancia._descuento_aplicado = datos.get("descuento_aplicado", instancia._descuento_aplicado)
        instancia._costo_total = datos.get("costo_total", instancia._costo_total)

        return instancia
