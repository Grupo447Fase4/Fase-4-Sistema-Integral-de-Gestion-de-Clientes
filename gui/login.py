"""
forms.py — Formularios modales para creación de Clientes, Servicios y Reservas.

Librería `tkinter`: GUI nativa de Python para crear ventanas, widgets e interacciones.
Librería `tkinter.ttk`: Versión temática de tkinter con widgets modernos (Combobox, etc.).
Librería `tkinter.messagebox`: Diálogos estándar de alerta, error y confirmación.
Librería `typing`: Anotaciones de tipos para mayor claridad.
"""

import tkinter as tk                         # Framework GUI principal
from tkinter import ttk, messagebox          # Widgets temáticos y diálogos
from typing import Optional, Callable, Any   # Tipado fuerte
from datetime import datetime                # Para valor inicial de fecha

# Importaciones del núcleo de negocio
from core.clients import ClienteCorriente, ClienteRegular, ClienteVIP
from core.services import ReservaSala, AlquilerEquipo, AsesoriaEspecializada
from core.reservations import Reserva
from core.base_models import ClienteBase, ServicioBase
from data.logger import logger

# ── Paleta de colores centralizada (consistencia visual) ──
COLORES = {
    "fondo": "#0D1117",           # Fondo principal oscuro
    "superficie": "#161B22",      # Cards y paneles
    "borde": "#30363D",           # Bordes sutiles
    "acento": "#58A6FF",          # Azul corporativo
    "acento2": "#3FB950",         # Verde para éxito
    "rojo": "#F85149",            # Rojo para cancelar/error
    "texto": "#C9D1D9",           # Texto principal
    "texto_dim": "#8B949E",       # Texto secundario
    "amarillo": "#D29922",        # Advertencias / VIP
    "input_bg": "#21262D",        # Fondo de inputs
    "btn_hover": "#1F6FEB",       # Hover de botones
}


def _crear_campo(frame: tk.Frame, label: str, row: int, ancho: int = 35,
                 placeholder: str = "") -> tk.Entry:
    """
    Función utilitaria: crea un par (Label + Entry) con estilo uniforme.

    Args:
        frame: Contenedor donde se crea el campo.
        label: Texto descriptivo del campo.
        row: Fila del grid donde se coloca.
        ancho: Ancho del Entry en caracteres.
        placeholder: Texto de ayuda visible si el campo está vacío.

    Returns:
        tk.Entry: El campo de entrada creado.
    """
    tk.Label(
        frame, text=label, bg=COLORES["superficie"],
        fg=COLORES["texto_dim"], font=("Consolas", 9),
        anchor="w"
    ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=(8, 0))

    entry = tk.Entry(
        frame, width=ancho, bg=COLORES["input_bg"],
        fg=COLORES["texto"], insertbackground=COLORES["acento"],
        relief="flat", font=("Consolas", 10),
        highlightthickness=1, highlightcolor=COLORES["acento"],
        highlightbackground=COLORES["borde"]
    )
    entry.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=(8, 0))

    # Añadir placeholder si se especificó
    if placeholder:
        entry.insert(0, placeholder)
        entry.config(fg=COLORES["texto_dim"])

        def on_focus_in(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(fg=COLORES["texto"])

        def on_focus_out(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(fg=COLORES["texto_dim"])

        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)

    return entry


def _crear_combo(frame: tk.Frame, label: str, row: int,
                 valores: list, ancho: int = 33) -> ttk.Combobox:
    """Crea un par (Label + Combobox) estilizado."""
    tk.Label(
        frame, text=label, bg=COLORES["superficie"],
        fg=COLORES["texto_dim"], font=("Consolas", 9), anchor="w"
    ).grid(row=row, column=0, sticky="w", padx=(15, 5), pady=(8, 0))

    combo = ttk.Combobox(frame, values=valores, width=ancho,
                         state="readonly", font=("Consolas", 10))
    combo.grid(row=row, column=1, sticky="ew", padx=(5, 15), pady=(8, 0))
    combo.current(0)
    return combo


# ─────────────────────────────────────────────────────────────────────────────
# FORMULARIO: NUEVO CLIENTE
# ─────────────────────────────────────────────────────────────────────────────

class FormularioCliente(tk.Toplevel):
    """
    Ventana modal para crear un nuevo cliente.
    Hereda de tk.Toplevel para mostrarse sobre la ventana principal.
    """

    def __init__(self, parent: tk.Widget, callback: Callable[[ClienteBase], None]) -> None:
        """
        Args:
            parent: Ventana padre.
            callback: Función que recibe el cliente creado al guardar.
        """
        super().__init__(parent)
        self._callback = callback
        self._cliente_creado: Optional[ClienteBase] = None

        self._configurar_ventana()
        self._construir_ui()

    def _configurar_ventana(self) -> None:
        """Configura dimensiones, título y estilo de la ventana modal."""
        self.title("➕ Nuevo Cliente — Software FJ")
        self.geometry("480x520")
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self.grab_set()          # Bloquea la ventana padre mientras está abierta
        self.focus_set()

    def _construir_ui(self) -> None:
        """Construye todos los widgets del formulario."""
        # ── Encabezado ──
        header = tk.Frame(self, bg=COLORES["acento"], height=4)
        header.pack(fill="x")

        tk.Label(
            self, text="NUEVO CLIENTE", bg=COLORES["fondo"],
            fg=COLORES["acento"], font=("Consolas", 14, "bold")
        ).pack(pady=(20, 5))

        tk.Label(
            self, text="Complete los datos del nuevo cliente",
            bg=COLORES["fondo"], fg=COLORES["texto_dim"], font=("Consolas", 9)
        ).pack(pady=(0, 15))

        # ── Panel del formulario ──
        frame = tk.Frame(self, bg=COLORES["superficie"],
                         highlightbackground=COLORES["borde"],
                         highlightthickness=1)
        frame.pack(fill="both", padx=20, pady=5)
        frame.columnconfigure(1, weight=1)

        # Campos del formulario
        self._entry_nombre = _crear_campo(frame, "Nombre completo:", 0, placeholder="Ej: Juan Pérez")
        self._entry_email = _crear_campo(frame, "Email:", 1, placeholder="ejemplo@correo.com")
        self._entry_telefono = _crear_campo(frame, "Teléfono:", 2, placeholder="3001234567")

        # Selector de rol
        self._combo_rol = _crear_combo(
            frame, "Rol del cliente:", 3,
            ["corriente", "regular", "vip"]
        )
        self._combo_rol.bind("<<ComboboxSelected>>", self._on_rol_cambiado)

        # ── Campos opcionales que aparecen según el rol ──
        self._frame_extra = tk.Frame(frame, bg=COLORES["superficie"])
        self._frame_extra.grid(row=4, column=0, columnspan=2, sticky="ew")
        self._frame_extra.columnconfigure(1, weight=1)

        self._entry_extra1: Optional[tk.Entry] = None
        self._entry_extra2: Optional[tk.Entry] = None

        # ── Botones de acción ──
        frame_btns = tk.Frame(self, bg=COLORES["fondo"])
        frame_btns.pack(fill="x", padx=20, pady=20)

        tk.Button(
            frame_btns, text="✓  GUARDAR CLIENTE",
            bg=COLORES["acento2"], fg="white", font=("Consolas", 10, "bold"),
            relief="flat", cursor="hand2", pady=10,
            command=self._guardar
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            frame_btns, text="✕  CANCELAR",
            bg=COLORES["rojo"], fg="white", font=("Consolas", 10),
            relief="flat", cursor="hand2", pady=10,
            command=self.destroy
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _on_rol_cambiado(self, event: Any) -> None:
        """Muestra campos adicionales según el rol seleccionado."""
        # Limpiar frame de extras
        for widget in self._frame_extra.winfo_children():
            widget.destroy()
        self._entry_extra1 = None
        self._entry_extra2 = None

        rol = self._combo_rol.get()
        if rol == "regular":
            self._entry_extra1 = _crear_campo(
                self._frame_extra, "Reservas previas:", 0, placeholder="0"
            )
        elif rol == "vip":
            self._entry_extra1 = _crear_campo(
                self._frame_extra, "Empresa:", 0, placeholder="Nombre empresa (opcional)"
            )
            self._entry_extra2 = _crear_campo(
                self._frame_extra, "Crédito disponible:", 1, placeholder="0.00"
            )

    def _guardar(self) -> None:
        """Valida los datos e instancia el cliente correspondiente."""
        try:
            nombre = self._entry_nombre.get().strip()
            email = self._entry_email.get().strip()
            telefono = self._entry_telefono.get().strip()
            rol = self._combo_rol.get()

            # Validaciones básicas de UI (la clase también valida)
            if not nombre or nombre == "Ej: Juan Pérez":
                raise ValueError("El nombre es obligatorio.")
            if not email or email == "ejemplo@correo.com":
                raise ValueError("El email es obligatorio.")
            if not telefono or telefono == "3001234567":
                raise ValueError("El teléfono es obligatorio.")

            # Instanciar según el rol seleccionado (Polimorfismo)
            cliente: ClienteBase

            if rol == "corriente":
                cliente = ClienteCorriente(nombre, email, telefono)

            elif rol == "regular":
                reservas = 0
                if self._entry_extra1:
                    val = self._entry_extra1.get().strip()
                    if val and val != "0":
                        reservas = int(val)
                cliente = ClienteRegular(nombre, email, telefono, reservas)

            elif rol == "vip":
                empresa = ""
                credito = 0.0
                if self._entry_extra1:
                    empresa = self._entry_extra1.get().strip()
                    if empresa == "Nombre empresa (opcional)":
                        empresa = ""
                if self._entry_extra2:
                    val = self._entry_extra2.get().strip()
                    if val and val != "0.00":
                        credito = float(val)
                cliente = ClienteVIP(nombre, email, telefono, empresa, credito)
            else:
                raise ValueError(f"Rol no reconocido: {rol}")

            # Llamar al callback con el cliente creado
            self._callback(cliente)
            logger.info(f"Formulario: cliente '{nombre}' creado como {rol}.")
            self.destroy()

        except (ValueError, TypeError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            logger.warning(f"Error en formulario de cliente: {e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e), parent=self)
            logger.error(f"Error inesperado en formulario cliente: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# FORMULARIO: NUEVO SERVICIO
# ─────────────────────────────────────────────────────────────────────────────

class FormularioServicio(tk.Toplevel):
    """Ventana modal para crear un nuevo servicio."""

    def __init__(self, parent: tk.Widget, callback: Callable[[ServicioBase], None]) -> None:
        super().__init__(parent)
        self._callback = callback
        self._configurar_ventana()
        self._construir_ui()

    def _configurar_ventana(self) -> None:
        self.title("➕ Nuevo Servicio — Software FJ")
        self.geometry("500x580")
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self.grab_set()
        self.focus_set()

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=COLORES["acento2"], height=4).pack(fill="x")

        tk.Label(
            self, text="NUEVO SERVICIO", bg=COLORES["fondo"],
            fg=COLORES["acento2"], font=("Consolas", 14, "bold")
        ).pack(pady=(20, 5))

        frame = tk.Frame(self, bg=COLORES["superficie"],
                         highlightbackground=COLORES["borde"], highlightthickness=1)
        frame.pack(fill="both", padx=20, pady=5)
        frame.columnconfigure(1, weight=1)

        self._entry_nombre = _crear_campo(frame, "Nombre del servicio:", 0)
        self._entry_precio = _crear_campo(frame, "Precio/hora (COP):", 1, placeholder="50000")
        self._entry_desc = _crear_campo(frame, "Descripción:", 2)

        self._combo_tipo = _crear_combo(
            frame, "Tipo de servicio:", 3,
            ["sala", "equipo", "asesoria"]
        )
        self._combo_tipo.bind("<<ComboboxSelected>>", self._on_tipo_cambiado)

        self._frame_extra = tk.Frame(frame, bg=COLORES["superficie"])
        self._frame_extra.grid(row=4, column=0, columnspan=2, sticky="ew")
        self._frame_extra.columnconfigure(1, weight=1)

        self._widgets_extra: dict = {}
        self._on_tipo_cambiado(None)

        frame_btns = tk.Frame(self, bg=COLORES["fondo"])
        frame_btns.pack(fill="x", padx=20, pady=20)

        tk.Button(
            frame_btns, text="✓  GUARDAR SERVICIO",
            bg=COLORES["acento2"], fg="white", font=("Consolas", 10, "bold"),
            relief="flat", cursor="hand2", pady=10,
            command=self._guardar
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            frame_btns, text="✕  CANCELAR",
            bg=COLORES["rojo"], fg="white", font=("Consolas", 10),
            relief="flat", cursor="hand2", pady=10,
            command=self.destroy
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _on_tipo_cambiado(self, event: Any) -> None:
        """Muestra campos específicos según el tipo de servicio."""
        for w in self._frame_extra.winfo_children():
            w.destroy()
        self._widgets_extra.clear()

        tipo = self._combo_tipo.get()

        if tipo == "sala":
            self._widgets_extra["capacidad"] = _crear_campo(
                self._frame_extra, "Capacidad (personas):", 0, placeholder="10"
            )
            # Checkbox para proyector
            self._var_proyector = tk.BooleanVar()
            tk.Label(
                self._frame_extra, text="¿Tiene proyector?:",
                bg=COLORES["superficie"], fg=COLORES["texto_dim"],
                font=("Consolas", 9), anchor="w"
            ).grid(row=1, column=0, sticky="w", padx=(15, 5), pady=(8, 0))
            tk.Checkbutton(
                self._frame_extra, variable=self._var_proyector,
                bg=COLORES["superficie"], fg=COLORES["texto"],
                activebackground=COLORES["superficie"],
                selectcolor=COLORES["acento"]
            ).grid(row=1, column=1, sticky="w", padx=(5, 15), pady=(8, 0))

        elif tipo == "equipo":
            self._widgets_extra["tipo_equipo"] = _crear_combo(
                self._frame_extra, "Categoría equipo:", 0,
                ["laptop", "cámara", "proyector", "servidor", "otro"]
            )
            self._var_deposito = tk.BooleanVar()
            tk.Label(
                self._frame_extra, text="¿Requiere depósito?:",
                bg=COLORES["superficie"], fg=COLORES["texto_dim"],
                font=("Consolas", 9), anchor="w"
            ).grid(row=1, column=0, sticky="w", padx=(15, 5), pady=(8, 0))
            tk.Checkbutton(
                self._frame_extra, variable=self._var_deposito,
                bg=COLORES["superficie"], fg=COLORES["texto"],
                activebackground=COLORES["superficie"],
                selectcolor=COLORES["acento"]
            ).grid(row=1, column=1, sticky="w", padx=(5, 15), pady=(8, 0))
            self._widgets_extra["valor_deposito"] = _crear_campo(
                self._frame_extra, "Valor depósito (COP):", 2, placeholder="0"
            )

        elif tipo == "asesoria":
            self._widgets_extra["area"] = _crear_campo(
                self._frame_extra, "Área especialidad:", 0, placeholder="software, redes, etc."
            )
            self._widgets_extra["nivel"] = _crear_combo(
                self._frame_extra, "Nivel del asesor:", 1,
                ["junior", "senior", "experto"]
            )

    def _guardar(self) -> None:
        """Valida y crea el servicio correspondiente."""
        try:
            nombre = self._entry_nombre.get().strip()
            precio_str = self._entry_precio.get().strip()
            desc = self._entry_desc.get().strip()
            tipo = self._combo_tipo.get()

            if not nombre:
                raise ValueError("El nombre del servicio es obligatorio.")
            precio_str_clean = precio_str.replace(",", "").replace(".", "")
            if not precio_str_clean.isdigit():
                raise ValueError("El precio debe ser un número entero válido.")
            precio = float(precio_str_clean)

            servicio: ServicioBase

            if tipo == "sala":
                cap_str = self._widgets_extra.get("capacidad")
                capacidad = int(cap_str.get() or "10") if cap_str else 10
                proyector = getattr(self, "_var_proyector", tk.BooleanVar()).get()
                servicio = ReservaSala(nombre, precio, desc, capacidad, proyector)

            elif tipo == "equipo":
                cat_combo = self._widgets_extra.get("tipo_equipo")
                cat = cat_combo.get() if cat_combo else "otro"
                req_dep = getattr(self, "_var_deposito", tk.BooleanVar()).get()
                dep_entry = self._widgets_extra.get("valor_deposito")
                dep_val = float(dep_entry.get() or "0") if dep_entry else 0.0
                servicio = AlquilerEquipo(nombre, precio, desc, cat, req_dep, dep_val)

            elif tipo == "asesoria":
                area_entry = self._widgets_extra.get("area")
                area = area_entry.get().strip() if area_entry else "general"
                nivel_combo = self._widgets_extra.get("nivel")
                nivel = nivel_combo.get() if nivel_combo else "senior"
                servicio = AsesoriaEspecializada(nombre, precio, desc, area, nivel)
            else:
                raise ValueError(f"Tipo desconocido: {tipo}")

            self._callback(servicio)
            logger.info(f"Formulario: servicio '{nombre}' ({tipo}) creado.")
            self.destroy()

        except (ValueError, TypeError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            logger.warning(f"Error en formulario de servicio: {e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e), parent=self)
            logger.error(f"Error inesperado en formulario servicio: {e}")


# ─────────────────────────────────────────────────────────────────────────────
# FORMULARIO: NUEVA RESERVA
# ─────────────────────────────────────────────────────────────────────────────

class FormularioReserva(tk.Toplevel):
    """Ventana modal para crear una reserva integrando cliente y servicio."""

    def __init__(self, parent: tk.Widget,
                 clientes: list, servicios: list,
                 callback: Callable[[Reserva], None]) -> None:
        """
        Args:
            parent: Ventana padre.
            clientes: Lista de objetos ClienteBase disponibles.
            servicios: Lista de objetos ServicioBase disponibles.
            callback: Función que recibe la Reserva creada.
        """
        super().__init__(parent)
        self._clientes = clientes
        self._servicios = servicios
        self._callback = callback
        self._configurar_ventana()
        self._construir_ui()

    def _configurar_ventana(self) -> None:
        self.title("📅 Nueva Reserva — Software FJ")
        self.geometry("520x540")
        self.resizable(False, False)
        self.configure(bg=COLORES["fondo"])
        self.grab_set()
        self.focus_set()

    def _construir_ui(self) -> None:
        tk.Frame(self, bg=COLORES["amarillo"], height=4).pack(fill="x")

        tk.Label(
            self, text="NUEVA RESERVA", bg=COLORES["fondo"],
            fg=COLORES["amarillo"], font=("Consolas", 14, "bold")
        ).pack(pady=(20, 5))

        frame = tk.Frame(self, bg=COLORES["superficie"],
                         highlightbackground=COLORES["borde"], highlightthickness=1)
        frame.pack(fill="both", padx=20, pady=5)
        frame.columnconfigure(1, weight=1)

        # ── Selector de cliente ──
        nombres_clientes = [f"{c.nombre} [{c.rol}]" for c in self._clientes]
        if not nombres_clientes:
            nombres_clientes = ["(No hay clientes registrados)"]
        self._combo_cliente = _crear_combo(frame, "Cliente:", 0, nombres_clientes)

        # ── Selector de servicio ──
        nombres_servicios = [f"{s.nombre} [{s.tipo_servicio}]" for s in self._servicios]
        if not nombres_servicios:
            nombres_servicios = ["(No hay servicios registrados)"]
        self._combo_servicio = _crear_combo(frame, "Servicio:", 1, nombres_servicios)
        self._combo_servicio.bind("<<ComboboxSelected>>", self._actualizar_preview)
        self._combo_cliente.bind("<<ComboboxSelected>>", self._actualizar_preview)

        # ── Horas ──
        self._entry_horas = _crear_campo(frame, "Duración (horas):", 2, placeholder="1")

        # ── Fecha deseada ──
        self._entry_fecha = _crear_campo(
            frame, "Fecha deseada:", 3,
            placeholder=datetime.now().strftime("%Y-%m-%d %H:%M")
        )

        # ── Notas ──
        self._entry_notas = _crear_campo(frame, "Notas adicionales:", 4, placeholder="Opcional")

        # ── Preview de costo ──
        self._lbl_preview = tk.Label(
            frame, text="💰 Seleccione cliente y servicio para ver el costo estimado",
            bg=COLORES["superficie"], fg=COLORES["texto_dim"],
            font=("Consolas", 9), wraplength=430, justify="left"
        )
        self._lbl_preview.grid(row=5, column=0, columnspan=2,
                               padx=15, pady=(12, 8), sticky="w")

        # ── Botones ──
        frame_btns = tk.Frame(self, bg=COLORES["fondo"])
        frame_btns.pack(fill="x", padx=20, pady=20)

        tk.Button(
            frame_btns, text="📅  CREAR RESERVA",
            bg=COLORES["amarillo"], fg=COLORES["fondo"],
            font=("Consolas", 10, "bold"),
            relief="flat", cursor="hand2", pady=10,
            command=self._guardar
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        tk.Button(
            frame_btns, text="✕  CANCELAR",
            bg=COLORES["rojo"], fg="white", font=("Consolas", 10),
            relief="flat", cursor="hand2", pady=10,
            command=self.destroy
        ).pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _actualizar_preview(self, event: Any = None) -> None:
        """Actualiza el texto de costo estimado al cambiar cliente o servicio."""
        try:
            idx_c = self._combo_cliente.current()
            idx_s = self._combo_servicio.current()
            if idx_c < 0 or idx_s < 0:
                return
            if idx_c >= len(self._clientes) or idx_s >= len(self._servicios):
                return

            cliente = self._clientes[idx_c]
            servicio = self._servicios[idx_s]

            horas_str = self._entry_horas.get().strip()
            horas = float(horas_str) if horas_str and horas_str != "1" else 1.0

            costo_bruto = servicio.calcular_costo(horas)
            descuento = cliente.descuento
            costo_final = costo_bruto * (1 - descuento)

            self._lbl_preview.config(
                text=(f"💰 Costo base: ${costo_bruto:,.0f} | "
                      f"Descuento ({int(descuento*100)}%): -${costo_bruto*descuento:,.0f} | "
                      f"TOTAL: ${costo_final:,.0f}"),
                fg=COLORES["acento2"]
            )
        except (ValueError, IndexError):
            pass

    def _guardar(self) -> None:
        """Crea la reserva con los datos del formulario."""
        try:
            idx_c = self._combo_cliente.current()
            idx_s = self._combo_servicio.current()

            if idx_c < 0 or idx_c >= len(self._clientes):
                raise ValueError("Seleccione un cliente válido.")
            if idx_s < 0 or idx_s >= len(self._servicios):
                raise ValueError("Seleccione un servicio válido.")

            cliente = self._clientes[idx_c]
            servicio = self._servicios[idx_s]

            horas_str = self._entry_horas.get().strip()
            if not horas_str or horas_str == "1":
                horas = 1.0
            else:
                horas = float(horas_str)

            fecha = self._entry_fecha.get().strip()
            notas = self._entry_notas.get().strip()
            if notas == "Opcional":
                notas = ""

            reserva = Reserva(cliente, servicio, horas, fecha, notas)
            self._callback(reserva)
            logger.info(f"Formulario: reserva creada | {cliente.nombre} → {servicio.nombre}")
            self.destroy()

        except (ValueError, TypeError) as e:
            messagebox.showerror("Error de validación", str(e), parent=self)
            logger.warning(f"Error en formulario de reserva: {e}")
        except Exception as e:
            messagebox.showerror("Error inesperado", str(e), parent=self)
            logger.error(f"Error inesperado en formulario reserva: {e}")
