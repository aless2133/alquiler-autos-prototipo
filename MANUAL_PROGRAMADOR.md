# Manual de programador — Sprint 1

## Arquitectura

La solución utiliza una separación sencilla por capas:

- `ui/`: interfaz gráfica con Tkinter.
- `servicios.py`: reglas de negocio y acceso funcional a los módulos.
- `base_datos.py`: conexión e inicialización de SQLite.
- `validaciones.py`: validaciones de entrada.
- `seguridad.py`: generación y verificación de contraseñas.
- `modelos.py`: dataclasses de dominio.
- `app.py`: punto de entrada.

## Base de datos

SQLite crea automáticamente:

- `usuarios`
- `clientes`
- `reservas`
- `intentos_login`
- `auditoria`

La tabla `reservas` se mantiene mínima porque el Sprint 1 solo necesita consultar si un cliente tiene una reserva activa antes de inactivarlo.

## Seguridad

Las contraseñas no se almacenan en texto plano. Se genera un salt aleatorio y se utiliza PBKDF2-HMAC-SHA256.

El login utiliza un contador de intentos por usuario y aplica un bloqueo temporal de 60 segundos al alcanzar 5 fallos.

## Regla del último administrador

Antes de cambiar el estado o rol de un administrador activo se contabilizan los administradores activos. Si solo existe uno, el cambio que lo dejaría sin esa condición se rechaza.

## Ejecución

```bash
python app.py
```

No se instala ningún paquete adicional.
