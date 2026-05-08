import json
import os
import tkinter as tk
from tkinter import messagebox

C = {
    "fondo": "#0D1117",
    "superficie": "#161B22",
    "texto": "#C9D1D9",
    "texto_dim": "#8B949E",
    "acento": "#58A6FF",
    "acento2": "#3FB950",
    "rojo": "#F85149",
    "input_bg": "#21262D",
    "borde": "#30363D",
}


class VentanaLogin:
    """Pantalla de login que guarda usuarios en config.json."""

    def __init__(self) -> None:
        self._ruta_config = "config.json"
        self._usuario_valido = False
        self._root = tk.Tk()
        self._root.title("Ingreso — Software FJ")
        self._root.geometry("420x320")
        self._root.resizable(False, False)
        self._root.configure(bg=C["fondo"])

        self._usuario = tk.StringVar()
        self._password = tk.StringVar()

        self._construir_ui()

    def ejecutar(self) -> bool:
        self._root.mainloop()
        return self._usuario_valido

    def _construir_ui(self) -> None:
        panel = tk.Frame(self._root, bg=C["superficie"], bd=0,
                        highlightthickness=0)
        panel.place(relx=0.5, rely=0.5, anchor="center", width=380, height=280)

        tk.Label(
            panel,
            text="BIENVENIDO A SOFTWARE FJ",
            bg=C["superficie"], fg=C["acento"],
            font=("Consolas", 14, "bold")
        ).pack(pady=(18, 6))

        tk.Label(
            panel,
            text="Ingrese su usuario y contraseña para continuar",
            bg=C["superficie"], fg=C["texto_dim"],
            font=("Consolas", 9)
        ).pack(pady=(0, 16))

        form = tk.Frame(panel, bg=C["superficie"])
        form.pack(fill="x", padx=24)

        self._crear_campo(form, "Usuario", self._usuario)
        self._crear_campo(form, "Contraseña", self._password, show="*")

        botones = tk.Frame(panel, bg=C["superficie"])
        botones.pack(fill="x", padx=24, pady=(16, 0))

        tk.Button(
            botones,
            text="Iniciar sesión",
            bg=C["acento"], fg="white",
            font=("Consolas", 10, "bold"), relief="flat",
            activebackground=C["texto_dim"], cursor="hand2",
            command=self._iniciar_sesion
        ).pack(fill="x", pady=(0, 6))

        tk.Button(
            botones,
            text="Registrar / actualizar",
            bg=C["acento2"], fg="white",
            font=("Consolas", 10), relief="flat",
            activebackground=C["texto_dim"], cursor="hand2",
            command=self._registrar_usuario
        ).pack(fill="x")

        pie = tk.Frame(panel, bg=C["superficie"])
        pie.pack(fill="x", padx=24, pady=(14, 0))

        tk.Label(
            pie,
            text="Los datos se guardan en config.json",
            bg=C["superficie"], fg=C["texto_dim"],
            font=("Consolas", 8)
        ).pack(side="left")

        tk.Button(
            pie,
            text="Salir",
            bg=C["rojo"], fg="white",
            font=("Consolas", 8, "bold"), relief="flat",
            cursor="hand2",
            command=self._root.destroy
        ).pack(side="right")

    def _crear_campo(self, padre: tk.Frame, etiqueta: str,
                    variable: tk.StringVar, show: str = "") -> None:
        tk.Label(
            padre, text=etiqueta,
            bg=C["superficie"], fg=C["texto_dim"],
            font=("Consolas", 9)
        ).pack(anchor="w", pady=(0, 4))

        entrada = tk.Entry(
            padre,
            textvariable=variable,
            show=show,
            bg=C["input_bg"], fg=C["texto"],
            insertbackground=C["texto"],
            relief="flat", font=("Consolas", 10),
            highlightthickness=1, highlightbackground=C["borde"],
            highlightcolor=C["acento"]
        )
        entrada.pack(fill="x", pady=(0, 12))

    def _leer_datos(self) -> dict:
        if not os.path.exists(self._ruta_config):
            return {
                "clientes": [],
                "servicios": [],
                "reservas": [],
                "usuarios": []
            }

        try:
            with open(self._ruta_config, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except json.JSONDecodeError:
            return {
                "clientes": [],
                "servicios": [],
                "reservas": [],
                "usuarios": []
            }

        if "usuarios" not in datos:
            datos["usuarios"] = []

        return datos

    def _guardar_datos(self, usuarios: list) -> None:
        datos = self._leer_datos()
        datos["usuarios"] = usuarios
        with open(self._ruta_config, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)

    def _iniciar_sesion(self) -> None:
        nombre = self._usuario.get().strip()
        contrasena = self._password.get().strip()

        if not nombre or not contrasena:
            messagebox.showwarning("Atención", "Complete usuario y contraseña.")
            return

        datos = self._leer_datos()
        usuarios = datos.get("usuarios", [])

        for usuario in usuarios:
            stored_name = usuario.get("username") or usuario.get("nombre")
            if stored_name == nombre and usuario.get("password") == contrasena:
                self._usuario_valido = True
                self._root.destroy()
                return

        messagebox.showerror("Acceso denegado", "Usuario o contraseña incorrectos.")

    def _registrar_usuario(self) -> None:
        nombre = self._usuario.get().strip()
        contrasena = self._password.get().strip()

        if not nombre or not contrasena:
            messagebox.showwarning("Atención", "Complete usuario y contraseña.")
            return

        datos = self._leer_datos()
        usuarios = datos.get("usuarios", [])

        for usuario in usuarios:
            stored_name = usuario.get("username") or usuario.get("nombre")
            if stored_name == nombre:
                usuario["username"] = nombre
                usuario["password"] = contrasena
                self._guardar_datos(usuarios)
                messagebox.showinfo("Actualizado", "Contraseña actualizada correctamente.")
                return

        usuarios.append({"username": nombre, "password": contrasena})
        self._guardar_datos(usuarios)
        messagebox.showinfo("Registrado", "Usuario creado correctamente.")
