# Manual de usuario — Sprint 1

## 1. Inicio de sesión

Ejecute:

```bash
python app.py
```

Ingrese el usuario y la contraseña. Después de 5 intentos fallidos consecutivos se activa un bloqueo temporal de 60 segundos.

La sesión se cierra automáticamente después de 15 minutos sin actividad.

## 2. Usuarios internos

El menú **Gestión de usuarios** está disponible para administradores.

Puede crear y editar usuarios. Cada registro permite seleccionar:

- administrador
- empleado

Un administrador activo no puede dejar el sistema sin ningún otro administrador activo.

## 3. Clientes

En **Clientes** puede:

- registrar un cliente;
- buscar por nombre, cédula/RUC, teléfono o correo;
- editar sus datos;
- inactivar un cliente.

El sistema rechaza cédulas/RUC duplicados.

Un cliente no puede inactivarse cuando existe una reserva marcada internamente como `Activa`.

## 4. Cerrar sesión

Use **Cerrar sesión** en el menú lateral. La pantalla vuelve al login.
