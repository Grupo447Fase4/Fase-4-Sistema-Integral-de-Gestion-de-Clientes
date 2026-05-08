# ⬡ Software FJ — Sistema Integral de Gestión

Sistema de gestión empresarial desarrollado en **Python + Tkinter**, con persistencia en JSON y registro de eventos en logs.

---

## 🗂 Arquitectura del Proyecto

```
SoftwareFJ/
│
├── main.py                 # Punto de entrada de la aplicación
├── config.json             # Persistencia de datos (generado automáticamente)
├── app.log                 # Registro de eventos y errores
│
├── core/                   # Lógica de negocio
│   ├── __init__.py
│   ├── base_models.py      # Clases abstractas: EntidadBase, ClienteBase, ServicioBase
│   ├── clients.py          # ClienteCorriente, ClienteRegular, ClienteVIP
│   ├── services.py         # ReservaSala, AlquilerEquipo, AsesoriaEspecializada
│   └── reservations.py     # Clase Reserva con ciclo de vida completo
│
├── data/                   # Capa de persistencia
│   ├── __init__.py
│   ├── json_manager.py     # GestorJSON: lectura/escritura con excepciones
│   └── logger.py           # Configuración del sistema de logs
│
└── gui/                    # Interfaz gráfica Tkinter
    ├── __init__.py
    ├── login.py            # Login
    ├── main_window.py      # VentanaPrincipal con 3 
    └── forms.py            # Formularios modales de creación
```

---

## 🚀 Ejecución

```bash
# Desde la carpeta SoftwareFJ/
python main.py
```

**Requisitos:** Python 3.8+ (solo librería estándar — sin dependencias externas)

---

## 🏛 Principios POO Aplicados

| Principio | Dónde se aplica |
|-----------|----------------|
| **Abstracción** | `EntidadBase`, `ClienteBase`, `ServicioBase` en `base_models.py` |
| **Herencia** | `ClienteCorriente`, `ClienteRegular`, `ClienteVIP` → `ClienteBase` |
| **Polimorfismo** | `rol`, `descuento`, `calcular_costo()`, `descripcion()` en cada subclase |
| **Encapsulación** | Atributos `_privados` con acceso via `@property` en todas las clases |

---

## 👥 Tipos de Cliente

| Rol | Descuento | Atributos Extras |
|-----|-----------|-----------------|
| Corriente | 0% | — |
| Regular | 10% | Contador de reservas |
| VIP | 25% | Empresa, crédito disponible |

---

## 🛠 Servicios Disponibles

| Servicio | Cálculo de Costo | Atributos Especiales |
|----------|-----------------|---------------------|
| Reserva de Sala | `precio/hora × horas + extra por personas` | Capacidad, proyector |
| Alquiler de Equipo | `precio/hora × horas` | Categoría, depósito |
| Asesoría Especializada | `precio/hora × horas × multiplicador_nivel` | Área, nivel (junior/senior/experto) |

---

## 📅 Ciclo de Vida de una Reserva

```
CREAR → pendiente ──→ confirmada ──→ cancelada
                  └──────────────→ cancelada
```

- **Confirmar**: Solo desde estado `pendiente`
- **Cancelar**: Desde `pendiente` o `confirmada`
- `cancelada` es estado **terminal** (no admite más cambios)

---

## 🔒 Manejo de Excepciones

| Excepción | Módulo | Cuándo se lanza |
|-----------|--------|----------------|
| `ErrorLecturaDatos` | `json_manager.py` | No se puede abrir el archivo JSON |
| `ErrorEscrituraDatos` | `json_manager.py` | No se puede escribir en el JSON |
| `ErrorDatosCorruptos` | `json_manager.py` | El JSON tiene formato inválido |
| `ErrorReservaInvalida` | `reservations.py` | Datos insuficientes para crear reserva |
| `ErrorTransicionEstado` | `reservations.py` | Cambio de estado no permitido |

---

## 📋 Logs

El archivo `app.log` registra todos los eventos:
```
[2024-01-15 10:30:00] [INFO    ] Cliente corriente creado: Juan Pérez
[2024-01-15 10:31:00] [INFO    ] Reserva CREADA | ID: a1b2c3d4 | ...
[2024-01-15 10:32:00] [INFO    ] Reserva a1b2c3d4 | Estado: pendiente → confirmada
[2024-01-15 10:33:00] [WARNING ] Error en formulario de cliente: Email inválido
```

---

## 📦 Persistencia JSON

Estructura del `config.json`:

```json
{
    "clientes": [
        {
            "id": "uuid4-generado",
            "nombre": "María García",
            "email": "maria@empresa.com",
            "telefono": "3001234567",
            "rol": "vip",
            "descuento": 0.25,
            "empresa": "Tech Corp",
            "credito_disponible": 500000.0,
            "activo": true,
            "fecha_creacion": "2024-01-15T10:30:00"
        }
    ],
    "servicios": [...],
    "reservas": [...]
}
```

---

*Desarrollado con Python 3.13.5 | Tkinter | JSON | Logging*
