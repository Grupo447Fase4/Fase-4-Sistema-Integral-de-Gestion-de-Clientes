"""
main_window.py — Ventana principal de la aplicación Software FJ.

Orquesta todos los módulos: carga datos desde JSON, presenta la UI principal
con sus pestañas y delega la creación de entidades a los formularios.

Librería `tkinter`: Framework GUI nativo de Python.
Librería `tkinter.ttk`: Widgets modernos y temas visuales.
Librería `tkinter.messagebox`: Diálogos de confirmación y alerta.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
import os

# Módulos del sistema
from core.clients import ClienteBase, cliente_desde_dict
from core.services import ServicioBase, servicio_desde_dict
from core.reservations import Reserva, ErrorReservaInvalida, ErrorTransicionEstado
from data.json_manager import GestorJSON
from data.logger import logger
from gui.forms import FormularioCliente, FormularioServicio, FormularioReserva

# ── Paleta de colores (idéntica a forms.py para coherencia visual) ──
C = {
    "fondo": "#0D1117",
    "superficie": "#161B22",
    "borde": "#30363D",
    "acento": "#58A6FF",
    "acento2": "#3FB950",
    "rojo": "#F85149",
    "texto": "#C9D1D9",
    "texto_dim": "#8B949E",
    "amarillo": "#D29922",
    "input_bg": "#21262D",
    "vip_gold": "#FFD700",
    "sidebar": "#010409",
}

# ── Estilos para el widget Treeview (tabla de datos) ──
def _aplicar_estilos_ttk(root: tk.Tk) -> None:
    """Configura el tema visual para los widgets ttk."""
    estilo = ttk.Style(root)
    estilo.theme_use("clam")

    # Treeview (tabla)
    estilo.configure("Treeview",
                     background=C["superficie"],
                     foreground=C["texto"],
                     fieldbackground=C["superficie"],
                     rowheight=30,
                     font=("Consolas", 10),
                     borderwidth=0)
    estilo.configure("Treeview.Heading",
                     background=C["fondo"],
                     foreground=C["acento"],
                     font=("Consolas", 10, "bold"),
                     relief="flat")
    estilo.map("Treeview",
               background=[("selected", C["acento"])],
               foreground=[("selected", "white")])

    # Pestañas (Notebook)
    estilo.configure("TNotebook",
                     background=C["fondo"],
                     borderwidth=0)
    estilo.configure("TNotebook.Tab",
                     background=C["superficie"],
                     foreground=C["texto_dim"],
                     padding=[20, 8],
                     font=("Consolas", 10))
    estilo.map("TNotebook.Tab",
               background=[("selected", C["acento"])],
               foreground=[("selected", "white")])

    # Scrollbar
    estilo.configure("Vertical.TScrollbar",
                     background=C["superficie"],
                     troughcolor=C["fondo"],
                     borderwidth=0)


class VentanaPrincipal:
    """
    Clase controladora de la ventana principal de Software FJ.
    Gestiona el ciclo de vida de la UI y coordina datos con persistencia.
    """

    def __init__(self) -> None:
        """Inicializa la ventana, carga datos y construye la interfaz."""
        # ── Listas en memoria (gestión interna con objetos Python) ──
        self._clientes: List[ClienteBase] = []
        self._servicios: List[ServicioBase] = []
        self._reservas: List[Reserva] = []

        # ── Capa de persistencia ──
        self._gestor: GestorJSON = GestorJSON("config.json")

        # ── Configurar ventana raíz ──
        self._root = tk.Tk()
        self._root.title("Software FJ — Sistema de Gestión")
        self._root.geometry("1100x700")
        self._root.minsize(900, 600)
        self._root.configure(bg=C["fondo"])

        # Intentar poner ícono si existe
        try:
            self._root.iconbitmap("icon.ico")
        except Exception:
            pass

        _aplicar_estilos_ttk(self._root)
        self._cargar_datos()
        self._construir_ui()
        logger.info("Ventana principal inicializada correctamente.")

    # ─────────────────────────────────────────────────────────────────────────
    # PERSISTENCIA: Carga y guardado
    # ─────────────────────────────────────────────────────────────────────────

    def _cargar_datos(self) -> None:
        """Lee el archivo JSON y reconstruye los objetos en memoria."""
        try:
            datos = self._gestor.leer()

            self._clientes = [cliente_desde_dict(c) for c in datos.get("clientes", [])]
            self._servicios = [servicio_desde_dict(s) for s in datos.get("servicios", [])]
            self._reservas = [Reserva.from_dict(r) for r in datos.get("reservas", [])]

            logger.info(
                f"Datos cargados: {len(self._clientes)} clientes, "
                f"{len(self._servicios)} servicios, {len(self._reservas)} reservas."
            )
        except Exception as e:
            logger.error(f"Error al cargar datos: {e}")
            messagebox.showerror("Error al cargar", f"No se pudieron cargar los datos:\n{e}")

    def _guardar_datos(self) -> None:
        """Serializa todos los objetos y los escribe en config.json."""
        try:
            self._gestor.guardar_sección("clientes", [c.to_dict() for c in self._clientes])
            self._gestor.guardar_sección("servicios", [s.to_dict() for s in self._servicios])
            self._gestor.guardar_sección("reservas", [r.to_dict() for r in self._reservas])
            logger.debug("Datos guardados exitosamente.")
        except Exception as e:
            logger.error(f"Error al guardar: {e}")
            messagebox.showerror("Error al guardar", str(e))

    # ─────────────────────────────────────────────────────────────────────────
    # CONSTRUCCIÓN DE LA INTERFAZ
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_ui(self) -> None:
        """Construye toda la interfaz: header, sidebar, contenido central."""
        self._construir_header()
        self._construir_contenido()
        self._construir_statusbar()

    def _construir_header(self) -> None:
        """Barra superior con logo y controles globales."""
        header = tk.Frame(self._root, bg=C["sidebar"], height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Borde inferior decorativo
        tk.Frame(header, bg=C["acento"], height=2).pack(side="bottom", fill="x")

        # Logo / Título
        tk.Label(
            header,
            text="⬡  SOFTWARE FJ",
            bg=C["sidebar"], fg=C["acento"],
            font=("Consolas", 16, "bold")
        ).pack(side="left", padx=25, pady=15)

        tk.Label(
            header, text="Sistema Integral de Gestión",
            bg=C["sidebar"], fg=C["texto_dim"],
            font=("Consolas", 9)
        ).pack(side="left", padx=(0, 30), pady=18)

        # Botón recargar
        tk.Button(
            header, text="⟳  Recargar",
            bg=C["superficie"], fg=C["texto"],
            relief="flat", cursor="hand2",
            font=("Consolas", 9), padx=12, pady=6,
            command=self._recargar_todo
        ).pack(side="right", padx=10, pady=12)

    def _construir_contenido(self) -> None:
        """Área central con pestañas: Clientes / Servicios / Reservas."""
        contenedor = tk.Frame(self._root, bg=C["fondo"])
        contenedor.pack(fill="both", expand=True, padx=15, pady=10)

        notebook = ttk.Notebook(contenedor)
        notebook.pack(fill="both", expand=True)

        # ── Pestaña 1: Clientes ──
        frame_clientes = tk.Frame(notebook, bg=C["fondo"])
        notebook.add(frame_clientes, text="  👤 CLIENTES  ")
        self._construir_tab_clientes(frame_clientes)

        # ── Pestaña 2: Servicios ──
        frame_servicios = tk.Frame(notebook, bg=C["fondo"])
        notebook.add(frame_servicios, text="  🛠  SERVICIOS  ")
        self._construir_tab_servicios(frame_servicios)

        # ── Pestaña 3: Reservas ──
        frame_reservas = tk.Frame(notebook, bg=C["fondo"])
        notebook.add(frame_reservas, text="  📅 RESERVAS  ")
        self._construir_tab_reservas(frame_reservas)

    def _construir_statusbar(self) -> None:
        """Barra inferior con estadísticas en tiempo real."""
        self._statusbar = tk.Frame(self._root, bg=C["sidebar"], height=28)
        self._statusbar.pack(fill="x", side="bottom")
        tk.Frame(self._statusbar, bg=C["borde"], height=1).pack(fill="x")

        self._lbl_status = tk.Label(
            self._statusbar,
            text="Listo", bg=C["sidebar"],
            fg=C["texto_dim"], font=("Consolas", 8),
            anchor="w"
        )
        self._lbl_status.pack(side="left", padx=15, pady=4)
        self._actualizar_status()

    def _actualizar_status(self) -> None:
        """Refresca las estadísticas en la barra inferior."""
        pendientes = sum(1 for r in self._reservas if r.estado == "pendiente")
        confirmadas = sum(1 for r in self._reservas if r.estado == "confirmada")
        self._lbl_status.config(
            text=(f"  Clientes: {len(self._clientes)}  │  "
                  f"Servicios: {len(self._servicios)}  │  "
                  f"Reservas: {len(self._reservas)}  "
                  f"(Pendientes: {pendientes}  │  Confirmadas: {confirmadas})")
        )

    # ─────────────────────────────────────────────────────────────────────────
    # TAB CLIENTES
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_tab_clientes(self, parent: tk.Frame) -> None:
        """Construye la pestaña de gestión de clientes."""
        self._construir_barra_acciones(
            parent,
            titulo="Gestión de Clientes",
            btn_nuevo_texto="➕  Nuevo Cliente",
            btn_nuevo_cmd=self._abrir_form_cliente,
            btn_eliminar_cmd=self._eliminar_cliente
        )

        columnas = ("nombre", "email", "telefono", "rol", "descuento", "estado")
        self._tree_clientes = self._crear_treeview(
            parent, columnas,
            {"nombre": ("Nombre", 200), "email": ("Email", 200),
             "telefono": ("Teléfono", 110), "rol": ("Rol", 90),
             "descuento": ("Descuento", 80), "estado": ("Estado", 80)}
        )
        self._refrescar_tabla_clientes()

    def _refrescar_tabla_clientes(self) -> None:
        """Limpia y repobla la tabla de clientes desde la lista en memoria."""
        tree = self._tree_clientes
        for item in tree.get_children():
            tree.delete(item)

        for cliente in self._clientes:
            # Color por rol (tag de color)
            tag = cliente.rol
            tree.insert("", "end", values=(
                cliente.nombre,
                cliente.email,
                cliente.telefono,
                cliente.rol.upper(),
                f"{int(cliente.descuento * 100)}%",
                "✅ Activo" if cliente.activo else "❌ Inactivo"
            ), tags=(tag,))

        # Colores diferenciados por rol
        tree.tag_configure("corriente", foreground=C["texto"])
        tree.tag_configure("regular", foreground=C["acento"])
        tree.tag_configure("vip", foreground=C["vip_gold"])

    def _abrir_form_cliente(self) -> None:
        """Abre el formulario modal para crear un nuevo cliente."""
        def al_guardar(cliente: ClienteBase) -> None:
            self._clientes.append(cliente)
            self._guardar_datos()
            self._refrescar_tabla_clientes()
            self._actualizar_status()
            messagebox.showinfo("Éxito", f"Cliente '{cliente.nombre}' creado correctamente.")

        FormularioCliente(self._root, callback=al_guardar)

    def _eliminar_cliente(self) -> None:
        """Elimina el cliente seleccionado en la tabla."""
        tree = self._tree_clientes
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un cliente de la tabla.")
            return

        idx = tree.index(seleccion[0])
        cliente = self._clientes[idx]

        # Verificar si tiene reservas activas
        reservas_activas = [r for r in self._reservas
                            if r.cliente.id == cliente.id and r.estado != "cancelada"]
        if reservas_activas:
            messagebox.showerror(
                "No permitido",
                f"El cliente '{cliente.nombre}' tiene {len(reservas_activas)} reserva(s) activa(s).\n"
                "Cancele las reservas antes de eliminar el cliente."
            )
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar cliente '{cliente.nombre}'?"):
            self._clientes.pop(idx)
            self._guardar_datos()
            self._refrescar_tabla_clientes()
            self._actualizar_status()
            logger.info(f"Cliente eliminado: {cliente.nombre}")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB SERVICIOS
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_tab_servicios(self, parent: tk.Frame) -> None:
        self._construir_barra_acciones(
            parent,
            titulo="Gestión de Servicios",
            btn_nuevo_texto="➕  Nuevo Servicio",
            btn_nuevo_cmd=self._abrir_form_servicio,
            btn_eliminar_cmd=self._eliminar_servicio
        )

        columnas = ("nombre", "tipo", "precio", "descripcion", "disponible")
        self._tree_servicios = self._crear_treeview(
            parent, columnas,
            {"nombre": ("Nombre", 200), "tipo": ("Tipo", 100),
             "precio": ("Precio/hora", 120), "descripcion": ("Descripción", 250),
             "disponible": ("Disponible", 90)}
        )
        self._refrescar_tabla_servicios()

    def _refrescar_tabla_servicios(self) -> None:
        tree = self._tree_servicios
        for item in tree.get_children():
            tree.delete(item)

        iconos_tipo = {"sala": "🏢", "equipo": "💻", "asesoria": "🎓"}

        for servicio in self._servicios:
            icono = iconos_tipo.get(servicio.tipo_servicio, "📦")
            tree.insert("", "end", values=(
                servicio.nombre,
                f"{icono} {servicio.tipo_servicio.upper()}",
                f"${servicio.precio_hora:,.0f}",
                servicio.descripcion_servicio or "—",
                "✅ Sí" if servicio.disponible else "❌ No"
            ))

    def _abrir_form_servicio(self) -> None:
        def al_guardar(servicio: ServicioBase) -> None:
            self._servicios.append(servicio)
            self._guardar_datos()
            self._refrescar_tabla_servicios()
            self._actualizar_status()
            messagebox.showinfo("Éxito", f"Servicio '{servicio.nombre}' creado correctamente.")

        FormularioServicio(self._root, callback=al_guardar)

    def _eliminar_servicio(self) -> None:
        tree = self._tree_servicios
        seleccion = tree.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione un servicio de la tabla.")
            return

        idx = tree.index(seleccion[0])
        servicio = self._servicios[idx]

        reservas_activas = [r for r in self._reservas
                            if r.servicio.id == servicio.id and r.estado != "cancelada"]
        if reservas_activas:
            messagebox.showerror(
                "No permitido",
                f"El servicio '{servicio.nombre}' tiene {len(reservas_activas)} reserva(s) activa(s)."
            )
            return

        if messagebox.askyesno("Confirmar", f"¿Eliminar servicio '{servicio.nombre}'?"):
            self._servicios.pop(idx)
            self._guardar_datos()
            self._refrescar_tabla_servicios()
            logger.info(f"Servicio eliminado: {servicio.nombre}")

    # ─────────────────────────────────────────────────────────────────────────
    # TAB RESERVAS
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_tab_reservas(self, parent: tk.Frame) -> None:
        """Construye la pestaña de reservas con panel de detalle y acciones."""
        # Barra de acciones
        barra = tk.Frame(parent, bg=C["fondo"])
        barra.pack(fill="x", pady=(10, 5))

        tk.Label(
            barra, text="Gestión de Reservas",
            bg=C["fondo"], fg=C["texto"],
            font=("Consolas", 12, "bold")
        ).pack(side="left", padx=15)

        tk.Button(
            barra, text="➕  Nueva Reserva",
            bg=C["amarillo"], fg=C["fondo"],
            font=("Consolas", 9, "bold"),
            relief="flat", cursor="hand2", padx=12, pady=6,
            command=self._abrir_form_reserva
        ).pack(side="right", padx=5)

        tk.Button(
            barra, text="✓  Confirmar",
            bg=C["acento2"], fg="white",
            font=("Consolas", 9), relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._confirmar_reserva
        ).pack(side="right", padx=5)

        tk.Button(
            barra, text="✕  Cancelar",
            bg=C["rojo"], fg="white",
            font=("Consolas", 9), relief="flat", cursor="hand2",
            padx=12, pady=6,
            command=self._cancelar_reserva
        ).pack(side="right", padx=5)

        # ── Tabla de reservas ──
        columnas = ("cliente", "rol", "servicio", "horas", "fecha", "costo", "estado")
        self._tree_reservas = self._crear_treeview(
            parent, columnas,
            {"cliente": ("Cliente", 160), "rol": ("Rol", 80),
             "servicio": ("Servicio", 160), "horas": ("Horas", 60),
             "fecha": ("Fecha Reserva", 150), "costo": ("Total", 110),
             "estado": ("Estado", 100)}
        )

        # ── Panel de detalle (aparece al seleccionar una reserva) ──
        self._frame_detalle = tk.Frame(parent, bg=C["superficie"],
                                       highlightbackground=C["borde"],
                                       highlightthickness=1)
        self._frame_detalle.pack(fill="x", padx=15, pady=(5, 10))

        self._lbl_detalle = tk.Label(
            self._frame_detalle,
            text="Seleccione una reserva para ver el detalle completo.",
            bg=C["superficie"], fg=C["texto_dim"],
            font=("Consolas", 9), justify="left", padx=15, pady=8
        )
        self._lbl_detalle.pack(anchor="w")

        self._tree_reservas.bind("<<TreeviewSelect>>", self._on_reserva_seleccionada)
        self._refrescar_tabla_reservas()

    def _refrescar_tabla_reservas(self) -> None:
        tree = self._tree_reservas
        for item in tree.get_children():
            tree.delete(item)

        iconos_estado = {
            "pendiente": "🟡 PENDIENTE",
            "confirmada": "🟢 CONFIRMADA",
            "cancelada": "🔴 CANCELADA"
        }

        for reserva in self._reservas:
            tag = reserva.estado
            tree.insert("", "end", values=(
                reserva.cliente.nombre,
                reserva.cliente.rol.upper(),
                reserva.servicio.nombre,
                f"{reserva.horas}h",
                reserva.fecha_reserva[:16],
                f"${reserva.costo_total:,.0f}",
                iconos_estado.get(reserva.estado, reserva.estado)
            ), tags=(tag,))

        tree.tag_configure("pendiente", foreground=C["amarillo"])
        tree.tag_configure("confirmada", foreground=C["acento2"])
        tree.tag_configure("cancelada", foreground=C["texto_dim"])

    def _on_reserva_seleccionada(self, event) -> None:
        """Muestra el detalle de la reserva seleccionada."""
        seleccion = self._tree_reservas.selection()
        if not seleccion:
            return
        idx = self._tree_reservas.index(seleccion[0])
        if idx >= len(self._reservas):
            return
        reserva = self._reservas[idx]
        self._lbl_detalle.config(
            text=reserva.resumen(),
            fg=C["texto"]
        )

    def _abrir_form_reserva(self) -> None:
        if not self._clientes:
            messagebox.showwarning("Sin clientes", "Registre al menos un cliente primero.")
            return
        if not self._servicios:
            messagebox.showwarning("Sin servicios", "Registre al menos un servicio primero.")
            return

        def al_guardar(reserva: Reserva) -> None:
            self._reservas.append(reserva)
            self._guardar_datos()
            self._refrescar_tabla_reservas()
            self._actualizar_status()
            messagebox.showinfo(
                "Reserva Creada",
                f"Reserva creada exitosamente.\n"
                f"Estado: PENDIENTE\n"
                f"Total: ${reserva.costo_total:,.0f}"
            )

        FormularioReserva(
            self._root,
            clientes=self._clientes,
            servicios=self._servicios,
            callback=al_guardar
        )

    def _confirmar_reserva(self) -> None:
        """Confirma la reserva seleccionada."""
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        try:
            reserva.confirmar("Confirmación desde interfaz")
            self._guardar_datos()
            self._refrescar_tabla_reservas()
            self._actualizar_status()
            messagebox.showinfo("Confirmada", f"La reserva ha sido CONFIRMADA.\nTotal: ${reserva.costo_total:,.0f}")
        except ErrorTransicionEstado as e:
            messagebox.showerror("No permitido", str(e))

    def _cancelar_reserva(self) -> None:
        """Cancela la reserva seleccionada."""
        reserva = self._obtener_reserva_seleccionada()
        if not reserva:
            return
        if not messagebox.askyesno("Confirmar cancelación", "¿Está seguro de cancelar esta reserva?"):
            return
        try:
            reserva.cancelar("Cancelación desde interfaz")
            self._guardar_datos()
            self._refrescar_tabla_reservas()
            self._actualizar_status()
            messagebox.showinfo("Cancelada", "La reserva ha sido CANCELADA.")
        except ErrorTransicionEstado as e:
            messagebox.showerror("No permitido", str(e))

    def _obtener_reserva_seleccionada(self) -> Optional[Reserva]:
        """Retorna la reserva actualmente seleccionada en la tabla."""
        seleccion = self._tree_reservas.selection()
        if not seleccion:
            messagebox.showwarning("Sin selección", "Seleccione una reserva de la tabla.")
            return None
        idx = self._tree_reservas.index(seleccion[0])
        if idx >= len(self._reservas):
            return None
        return self._reservas[idx]

    # ─────────────────────────────────────────────────────────────────────────
    # UTILIDADES UI
    # ─────────────────────────────────────────────────────────────────────────

    def _construir_barra_acciones(self, parent: tk.Frame, titulo: str,
                                   btn_nuevo_texto: str, btn_nuevo_cmd,
                                   btn_eliminar_cmd) -> None:
        """Crea la barra de acciones con título y botones Nuevo/Eliminar."""
        barra = tk.Frame(parent, bg=C["fondo"])
        barra.pack(fill="x", pady=(10, 5))

        tk.Label(
            barra, text=titulo,
            bg=C["fondo"], fg=C["texto"],
            font=("Consolas", 12, "bold")
        ).pack(side="left", padx=15)

        tk.Button(
            barra, text="🗑  Eliminar",
            bg=C["rojo"], fg="white",
            font=("Consolas", 9), relief="flat", cursor="hand2",
            padx=12, pady=6, command=btn_eliminar_cmd
        ).pack(side="right", padx=5)

        tk.Button(
            barra, text=btn_nuevo_texto,
            bg=C["acento"], fg="white",
            font=("Consolas", 9, "bold"),
            relief="flat", cursor="hand2",
            padx=12, pady=6, command=btn_nuevo_cmd
        ).pack(side="right", padx=5)

    def _crear_treeview(self, parent: tk.Frame, columnas: tuple,
                         config_cols: dict) -> ttk.Treeview:
        """
        Crea y configura un Treeview (tabla) con scroll vertical y horizontal.

        Args:
            parent: Contenedor padre.
            columnas: Tupla con IDs de columnas.
            config_cols: Dict {id: (encabezado, ancho)} para cada columna.

        Returns:
            ttk.Treeview: La tabla configurada.
        """
        contenedor = tk.Frame(parent, bg=C["fondo"])
        contenedor.pack(fill="both", expand=True, padx=15, pady=5)

        scroll_y = ttk.Scrollbar(contenedor, orient="vertical")
        scroll_x = ttk.Scrollbar(contenedor, orient="horizontal")

        tree = ttk.Treeview(
            contenedor, columns=columnas, show="headings",
            yscrollcommand=scroll_y.set,
            xscrollcommand=scroll_x.set,
            selectmode="browse"
        )

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)

        # Posicionar widgets en grid
        tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        contenedor.rowconfigure(0, weight=1)
        contenedor.columnconfigure(0, weight=1)

        # Configurar encabezados y anchos de columna
        for col_id, (encabezado, ancho) in config_cols.items():
            tree.heading(col_id, text=encabezado,
                         command=lambda c=col_id: self._ordenar_por(tree, c))
            tree.column(col_id, width=ancho, minwidth=50, anchor="w")

        return tree

    def _ordenar_por(self, tree: ttk.Treeview, columna: str) -> None:
        """Ordena la tabla por la columna clicada (toggle asc/desc)."""
        datos = [(tree.set(item, columna), item) for item in tree.get_children()]
        datos.sort(reverse=getattr(tree, "_orden_desc", False))
        for i, (_, item) in enumerate(datos):
            tree.move(item, "", i)
        tree._orden_desc = not getattr(tree, "_orden_desc", False)

    def _recargar_todo(self) -> None:
        """Recarga los datos desde disco y refresca todas las tablas."""
        self._cargar_datos()
        self._refrescar_tabla_clientes()
        self._refrescar_tabla_servicios()
        self._refrescar_tabla_reservas()
        self._actualizar_status()
        logger.info("Datos recargados manualmente desde la UI.")

    # ─────────────────────────────────────────────────────────────────────────
    # CICLO DE VIDA
    # ─────────────────────────────────────────────────────────────────────────

    def ejecutar(self) -> None:
        """Inicia el loop principal de la aplicación."""
        logger.info("Iniciando loop principal de la aplicación.")
        self._root.mainloop()
        logger.info("Aplicación cerrada.")
