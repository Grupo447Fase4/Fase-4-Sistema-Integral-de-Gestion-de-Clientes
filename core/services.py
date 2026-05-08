"""
services.py — Implementación concreta de los servicios de Software FJ.

Los tres servicios ofrecidos son:
1. ReservaSala     — Alquiler de salas de reunión/trabajo.
2. AlquilerEquipo  — Renta de equipos tecnológicos.
3. AsesoriaEspecializada — Consultoría técnica por hora.

Principio POLIMORFISMO: cada servicio calcula su costo de manera distinta
aunque todos exponen el mismo método `calcular_costo(horas)`.
"""

from typing import Dict, Any, List           # Tipado fuerte
from core.base_models import ServicioBase    # Clase abstracta padre
from data.logger import logger               # Sistema de logs


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 1: Reserva de Sala
# ─────────────────────────────────────────────────────────────────────────────

class ReservaSala(ServicioBase):
    """
    Servicio de reserva de salas de reunión o trabajo.
    Puede tener un cargo adicional según la capacidad de personas.
    """

    # Costo adicional por persona extra más allá de la capacidad base (5 personas)
    _COSTO_PERSONA_EXTRA: float = 15000.0      # COP por persona adicional

    def __init__(self, nombre: str, precio_hora: float, descripcion_servicio: str,
                 capacidad: int = 10, tiene_proyector: bool = False) -> None:
        """
        Crea un servicio de sala.

        Args:
            nombre (str): Nombre de la sala.
            precio_hora (float): Precio base por hora.
            descripcion_servicio (str): Descripción de la sala.
            capacidad (int): Número máximo de personas.
            tiene_proyector (bool): Si la sala incluye proyector.
        """
        super().__init__(nombre, precio_hora, descripcion_servicio)

        if not isinstance(capacidad, int) or capacidad < 1:
            raise ValueError("La capacidad debe ser un entero positivo.")

        self._capacidad: int = capacidad
        self._tiene_proyector: bool = bool(tiene_proyector)
        logger.info(f"Sala creada: '{nombre}' | Capacidad: {capacidad} | Proyector: {tiene_proyector}")

    @property
    def tipo_servicio(self) -> str:
        return "sala"

    @property
    def capacidad(self) -> int:
        return self._capacidad

    @property
    def tiene_proyector(self) -> bool:
        return self._tiene_proyector

    def calcular_costo(self, horas: float, personas: int = 1) -> float:
        """
        Calcula costo de la sala. Si hay más de 5 personas, cobra extra.

        Args:
            horas (float): Duración de la reserva.
            personas (int): Número de asistentes.

        Returns:
            float: Costo total en COP.
        """
        if horas <= 0:
            raise ValueError("Las horas deben ser positivas.")
        costo_base: float = self._precio_hora * horas
        # Cobro adicional por personas más allá del umbral base (5)
        personas_extra: int = max(0, personas - 5)
        costo_extra: float = personas_extra * self._COSTO_PERSONA_EXTRA
        return costo_base + costo_extra

    def descripcion(self) -> str:
        proyector_txt = "con proyector" if self._tiene_proyector else "sin proyector"
        return (f"[SALA] {self._nombre} | "
                f"Capacidad: {self._capacidad} personas | "
                f"{proyector_txt} | "
                f"${self._precio_hora:,.0f}/hora")

    def validar(self) -> bool:
        return self._capacidad > 0 and self._precio_hora > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "precio_hora": self._precio_hora,
            "descripcion_servicio": self._descripcion_servicio,
            "tipo_servicio": self.tipo_servicio,
            "capacidad": self._capacidad,
            "tiene_proyector": self._tiene_proyector,
            "disponible": self._disponible,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "ReservaSala":
        instancia = cls(
            nombre=datos["nombre"],
            precio_hora=datos["precio_hora"],
            descripcion_servicio=datos["descripcion_servicio"],
            capacidad=datos.get("capacidad", 10),
            tiene_proyector=datos.get("tiene_proyector", False)
        )
        instancia._id = datos["id"]
        instancia._disponible = datos.get("disponible", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 2: Alquiler de Equipo
# ─────────────────────────────────────────────────────────────────────────────

class AlquilerEquipo(ServicioBase):
    """
    Servicio de alquiler de equipos tecnológicos (laptops, cámaras, etc.).
    Puede aplicar un seguro adicional sobre el costo total.
    """

    def __init__(self, nombre: str, precio_hora: float, descripcion_servicio: str,
                 tipo_equipo: str = "general", requiere_deposito: bool = False,
                 valor_deposito: float = 0.0) -> None:
        """
        Crea un servicio de alquiler de equipo.

        Args:
            nombre (str): Nombre del equipo.
            precio_hora (float): Precio por hora de alquiler.
            descripcion_servicio (str): Descripción del equipo.
            tipo_equipo (str): Categoría (laptop, cámara, proyector, etc.).
            requiere_deposito (bool): Si se exige depósito de garantía.
            valor_deposito (float): Monto del depósito.
        """
        super().__init__(nombre, precio_hora, descripcion_servicio)

        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ValueError("El tipo de equipo no puede estar vacío.")
        if valor_deposito < 0:
            raise ValueError("El valor del depósito no puede ser negativo.")

        self._tipo_equipo: str = tipo_equipo.strip()
        self._requiere_deposito: bool = bool(requiere_deposito)
        self._valor_deposito: float = float(valor_deposito)
        logger.info(f"Equipo creado: '{nombre}' | Tipo: {tipo_equipo}")

    @property
    def tipo_servicio(self) -> str:
        return "equipo"

    @property
    def tipo_equipo(self) -> str:
        return self._tipo_equipo

    @property
    def requiere_deposito(self) -> bool:
        return self._requiere_deposito

    @property
    def valor_deposito(self) -> float:
        return self._valor_deposito

    def calcular_costo(self, horas: float) -> float:
        """
        Calcula el costo del alquiler (sin incluir depósito, que se devuelve).

        Args:
            horas (float): Número de horas de alquiler.

        Returns:
            float: Costo total sin depósito.
        """
        if horas <= 0:
            raise ValueError("Las horas deben ser positivas.")
        return self._precio_hora * horas

    def descripcion(self) -> str:
        deposito_txt = f"Depósito: ${self._valor_deposito:,.0f}" if self._requiere_deposito else "Sin depósito"
        return (f"[EQUIPO] {self._nombre} | "
                f"Tipo: {self._tipo_equipo} | "
                f"${self._precio_hora:,.0f}/hora | "
                f"{deposito_txt}")

    def validar(self) -> bool:
        return bool(self._tipo_equipo) and self._precio_hora > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "precio_hora": self._precio_hora,
            "descripcion_servicio": self._descripcion_servicio,
            "tipo_servicio": self.tipo_servicio,
            "tipo_equipo": self._tipo_equipo,
            "requiere_deposito": self._requiere_deposito,
            "valor_deposito": self._valor_deposito,
            "disponible": self._disponible,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "AlquilerEquipo":
        instancia = cls(
            nombre=datos["nombre"],
            precio_hora=datos["precio_hora"],
            descripcion_servicio=datos["descripcion_servicio"],
            tipo_equipo=datos.get("tipo_equipo", "general"),
            requiere_deposito=datos.get("requiere_deposito", False),
            valor_deposito=datos.get("valor_deposito", 0.0)
        )
        instancia._id = datos["id"]
        instancia._disponible = datos.get("disponible", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# SERVICIO 3: Asesoría Especializada
# ─────────────────────────────────────────────────────────────────────────────

class AsesoriaEspecializada(ServicioBase):
    """
    Servicio de consultoría o asesoría técnica especializada.
    Tiene una tarifa premium basada en el nivel del asesor.
    """

    # Multiplicadores de tarifa según nivel del asesor
    _MULTIPLICADORES: Dict[str, float] = {
        "junior": 1.0,    # Precio base
        "senior": 1.5,    # 50% más
        "experto": 2.0    # El doble
    }

    def __init__(self, nombre: str, precio_hora: float, descripcion_servicio: str,
                 area_especialidad: str = "general",
                 nivel_asesor: str = "senior") -> None:
        """
        Crea un servicio de asesoría.

        Args:
            nombre (str): Nombre de la asesoría.
            precio_hora (float): Precio base por hora.
            descripcion_servicio (str): Descripción del servicio.
            area_especialidad (str): Área temática (ej: 'software', 'redes').
            nivel_asesor (str): Nivel del asesor: 'junior', 'senior' o 'experto'.
        """
        super().__init__(nombre, precio_hora, descripcion_servicio)

        nivel = nivel_asesor.lower().strip()
        if nivel not in self._MULTIPLICADORES:
            raise ValueError(f"Nivel inválido: '{nivel_asesor}'. Use: {list(self._MULTIPLICADORES.keys())}")

        self._area_especialidad: str = area_especialidad.strip()
        self._nivel_asesor: str = nivel
        logger.info(f"Asesoría creada: '{nombre}' | Área: {area_especialidad} | Nivel: {nivel}")

    @property
    def tipo_servicio(self) -> str:
        return "asesoria"

    @property
    def area_especialidad(self) -> str:
        return self._area_especialidad

    @property
    def nivel_asesor(self) -> str:
        return self._nivel_asesor

    def calcular_costo(self, horas: float) -> float:
        """
        Calcula el costo aplicando el multiplicador según nivel del asesor.

        Args:
            horas (float): Horas de asesoría.

        Returns:
            float: Costo total ajustado por nivel.
        """
        if horas <= 0:
            raise ValueError("Las horas deben ser positivas.")
        multiplicador = self._MULTIPLICADORES[self._nivel_asesor]
        return self._precio_hora * horas * multiplicador

    def descripcion(self) -> str:
        return (f"[ASESORÍA] {self._nombre} | "
                f"Área: {self._area_especialidad} | "
                f"Nivel: {self._nivel_asesor.upper()} | "
                f"${self._precio_hora:,.0f}/hora base")

    def validar(self) -> bool:
        return bool(self._area_especialidad) and self._precio_hora > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._id,
            "nombre": self._nombre,
            "precio_hora": self._precio_hora,
            "descripcion_servicio": self._descripcion_servicio,
            "tipo_servicio": self.tipo_servicio,
            "area_especialidad": self._area_especialidad,
            "nivel_asesor": self._nivel_asesor,
            "disponible": self._disponible,
            "fecha_creacion": self._fecha_creacion
        }

    @classmethod
    def from_dict(cls, datos: Dict[str, Any]) -> "AsesoriaEspecializada":
        instancia = cls(
            nombre=datos["nombre"],
            precio_hora=datos["precio_hora"],
            descripcion_servicio=datos["descripcion_servicio"],
            area_especialidad=datos.get("area_especialidad", "general"),
            nivel_asesor=datos.get("nivel_asesor", "senior")
        )
        instancia._id = datos["id"]
        instancia._disponible = datos.get("disponible", True)
        instancia._fecha_creacion = datos.get("fecha_creacion", instancia._fecha_creacion)
        return instancia


# ─────────────────────────────────────────────────────────────────────────────
# FÁBRICA DE SERVICIOS
# Reconstruye el servicio correcto según el tipo almacenado en JSON.
# ─────────────────────────────────────────────────────────────────────────────

def servicio_desde_dict(datos: Dict[str, Any]) -> ServicioBase:
    """
    Reconstruye el objeto servicio correcto según el campo 'tipo_servicio'.

    Args:
        datos (Dict[str, Any]): Diccionario del JSON.

    Returns:
        ServicioBase: Instancia del tipo concreto correspondiente.

    Raises:
        ValueError: Si el tipo no es reconocido.
    """
    tipo: str = datos.get("tipo_servicio", "").lower()

    fabricas = {
        "sala": ReservaSala,
        "equipo": AlquilerEquipo,
        "asesoria": AsesoriaEspecializada
    }

    if tipo not in fabricas:
        raise ValueError(f"Tipo de servicio desconocido: '{tipo}'")

    return fabricas[tipo].from_dict(datos)
