# Sistema de Gestión — Sprint 1

Prototipo del Sprint 1 para el proyecto de software.

## Módulos implementados

- **HU-10 — Autenticación de usuarios**
  - Login con usuario y contraseña.
  - Contraseñas almacenadas mediante hash PBKDF2-HMAC-SHA256 (no texto plano).
  - Bloqueo temporal después de 5 intentos fallidos consecutivos.
  - Cierre automático de sesión después de 15 minutos de inactividad.

- **HU-09 — Gestionar usuarios internos y roles**
  - Crear, editar y desactivar usuarios internos.
  - Roles: `administrador` y `empleado`.
  - Restricción de acceso a gestión de usuarios por rol.
  - No permite desactivar/cambiar el rol del último administrador activo.

- **HU-01 — Gestión de clientes**
  - Registrar, editar e inactivar clientes.
  - Campos: nombre, cédula/RUC, teléfono y correo.
  - Validación de duplicados por cédula/RUC.
  - No permite inactivar clientes con reservas activas.

## Tecnologías

- Python 3
- Tkinter
- SQLite

No requiere dependencias externas.

## Estructura

```text
proyecto_sprint1/
├── app.py
├── base_datos.py
├── modelos.py
├── seguridad.py
├── servicios.py
├── validaciones.py
└── ui/
    ├── __init__.py
    ├── base.py
    └── principal.py
```

## Ejecución

```bash
python app.py
```

La base de datos `sprint1.db` se crea automáticamente al iniciar.

## Acceso inicial

```text
Usuario: admin
Contraseña: Admin123!
```

Este acceso se crea únicamente cuando la base está vacía.

## Nota de alcance

El proyecto se limita al Sprint 1 indicado en las historias de usuario. La tabla interna `reservas` existe únicamente para poder validar la regla de negocio de HU-01; no se implementó un módulo de reservas.
