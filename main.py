"""
main.py — Punto de entrada de la aplicación Software FJ.

Este archivo es el único que se ejecuta directamente:
    python main.py

Responsabilidades:
1. Ajustar el sys.path para que los imports relativos funcionen correctamente.
2. Capturar cualquier excepción fatal antes de que llegue al usuario sin mensaje.
3. Instanciar y ejecutar la ventana principal.

Librería `sys`: Acceso al intérprete de Python (sys.path, sys.exit).
Librería `os`: Manipulación del directorio de trabajo.
"""

import sys   # Módulo del intérprete: sys.path controla dónde Python busca módulos
import os    # Sistema de archivos: getcwd, path.join

# ── Asegurar que la raíz del proyecto esté en sys.path ──
# Esto permite que `from core.clients import ...` funcione sin importar
# desde qué directorio se ejecute el script.
directorio_raiz = os.path.dirname(os.path.abspath(__file__))
if directorio_raiz not in sys.path:
    sys.path.insert(0, directorio_raiz)

# ── Cambiar el directorio de trabajo a la raíz del proyecto ──
# Necesario para que config.json y app.log se creen en el lugar correcto.
os.chdir(directorio_raiz)

# ── Importaciones propias (después de ajustar sys.path) ──
from data.logger import logger          # Logger global
from gui.main_window import VentanaPrincipal  # Ventana principal
from gui.login import VentanaLogin      # Ventana de login



def main() -> None:
    """
    Función principal. Punto de entrada real del programa.
    Envuelta en try/except para capturar errores fatales de arranque.
    """
    logger.info("=" * 60)
    logger.info("  SOFTWARE FJ — Sistema de Gestión  v1.0")
    logger.info("=" * 60)
    logger.info(f"  Directorio de trabajo: {os.getcwd()}")

    try:
        login = VentanaLogin()
        if login.ejecutar():
            app = VentanaPrincipal()
            app.ejecutar()
        else:
            logger.info("Acceso no autorizado o se cerró el login. Saliendo.")
            return

    except ImportError as e:
        # Falta alguna dependencia o módulo del proyecto
        logger.critical(f"Error de importación fatal: {e}")
        print(f"\n[ERROR FATAL] Módulo no encontrado: {e}")
        print("Verifique que todos los archivos del proyecto están en su lugar.")
        sys.exit(1)

    except Exception as e:
        # Cualquier otro error inesperado durante el arranque
        logger.critical(f"Error fatal no controlado: {e}", exc_info=True)
        print(f"\n[ERROR FATAL] {e}")
        sys.exit(1)

    finally:
        logger.info("Software FJ cerrado.")


# ── Guardia de entrada principal ──
# Garantiza que main() solo se ejecute si corremos `python main.py` directamente,
# no cuando el módulo es importado por otro archivo.
if __name__ == "__main__":
    main()
