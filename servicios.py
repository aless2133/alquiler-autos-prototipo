import time
from base_datos import obtener_conexion, registrar_auditoria
from seguridad import verificar_password, generar_hash
from validaciones import (
    ErrorValidacion, validar_credenciales, validar_usuario_interno, validar_cliente
)

MAX_INTENTOS = 5
BLOQUEO_SEGUNDOS = 60

def _usuario(fila):
    return dict(fila) if fila else None

def autenticar(username, password):
    validar_credenciales(username, password)
    username = username.strip()
    ahora = time.time()
    with obtener_conexion() as db:
        control = db.execute(
            "SELECT intentos, bloqueado_hasta FROM intentos_login WHERE username=?",
            (username,)
        ).fetchone()
        if control and control["bloqueado_hasta"] > ahora:
            faltan = max(1, int(control["bloqueado_hasta"] - ahora))
            raise ErrorValidacion(f"Acceso bloqueado temporalmente. Espere {faltan}s.")
        fila = db.execute(
            "SELECT * FROM usuarios WHERE username=? COLLATE NOCASE", (username,)
        ).fetchone()
        correcto = fila and fila["estado"] == "Activo" and \
            verificar_password(password, fila["password_hash"])
        if correcto:
            db.execute("DELETE FROM intentos_login WHERE username=?", (username,))
            registrar_auditoria(db, "SEGURIDAD", "LOGIN", "Inicio de sesión exitoso", username)
            db.commit()
            return _usuario(fila)
        intentos = (control["intentos"] if control else 0) + 1
        bloqueado_hasta = ahora + BLOQUEO_SEGUNDOS if intentos >= MAX_INTENTOS else 0
        db.execute(
            """INSERT INTO intentos_login(username,intentos,bloqueado_hasta)
               VALUES(?,?,?)
               ON CONFLICT(username) DO UPDATE SET intentos=excluded.intentos,
               bloqueado_hasta=excluded.bloqueado_hasta""",
            (username, intentos, bloqueado_hasta)
        )
        db.commit()
    restantes = max(0, MAX_INTENTOS - intentos)
    if bloqueado_hasta:
        raise ErrorValidacion("Demasiados intentos fallidos. Acceso bloqueado por 60s.")
    raise ErrorValidacion(f"Credenciales inválidas. Intentos restantes: {restantes}.")

def listar_usuarios():
    with obtener_conexion() as db:
        rows = db.execute(
            "SELECT id_usuario,nombre,username,rol,estado,fecha_registro "
            "FROM usuarios ORDER BY id_usuario DESC"
        ).fetchall()
        return [dict(r) for r in rows]

def crear_usuario(datos, responsable):
    limpio = validar_usuario_interno(datos)
    with obtener_conexion() as db:
        if db.execute("SELECT 1 FROM usuarios WHERE username=? COLLATE NOCASE",
                      (limpio["username"],)).fetchone():
            raise ErrorValidacion("Ese nombre de usuario ya está registrado.")
        cur = db.execute(
            """INSERT INTO usuarios(nombre,username,password_hash,rol,estado)
               VALUES(?,?,?,?,?)""",
            (limpio["nombre"], limpio["username"], generar_hash(limpio["password"]),
             limpio["rol"], limpio["estado"])
        )
        registrar_auditoria(db, "USUARIOS", "CREAR",
                            f"Usuario {limpio['username']} creado.", responsable)
        db.commit()
        return cur.lastrowid

def actualizar_usuario(datos, responsable):
    limpio = validar_usuario_interno(datos, actualizacion=True)
    with obtener_conexion() as db:
        actual = db.execute("SELECT * FROM usuarios WHERE id_usuario=?",
                            (limpio["id_usuario"],)).fetchone()
        if not actual:
            raise ErrorValidacion("El usuario seleccionado no existe.")
        duplicado = db.execute(
            """SELECT 1 FROM usuarios WHERE username=? COLLATE NOCASE
               AND id_usuario<>?""", (limpio["username"], limpio["id_usuario"])
        ).fetchone()
        if duplicado:
            raise ErrorValidacion("Ese nombre de usuario ya está registrado.")
        if actual["rol"] == "administrador" and actual["estado"] == "Activo":
            quitandose_admin = limpio["rol"] != "administrador" or limpio["estado"] != "Activo"
            if quitandose_admin:
                admins = db.execute(
                    "SELECT COUNT(*) n FROM usuarios "
                    "WHERE rol='administrador' AND estado='Activo'"
                ).fetchone()["n"]
                if admins <= 1:
                    raise ErrorValidacion("No se puede eliminar o desactivar el último administrador.")
        if limpio["password"]:
            db.execute(
                """UPDATE usuarios SET nombre=?,username=?,password_hash=?,
                   rol=?,estado=? WHERE id_usuario=?""",
                (limpio["nombre"], limpio["username"], generar_hash(limpio["password"]),
                 limpio["rol"], limpio["estado"], limpio["id_usuario"])
            )
        else:
            db.execute(
                """UPDATE usuarios SET nombre=?,username=?,rol=?,estado=?
                   WHERE id_usuario=?""",
                (limpio["nombre"], limpio["username"], limpio["rol"],
                 limpio["estado"], limpio["id_usuario"])
            )
        registrar_auditoria(db, "USUARIOS", "EDITAR",
                            f"Usuario {limpio['username']} actualizado.", responsable)
        db.commit()

def obtener_usuario(id_usuario):
    with obtener_conexion() as db:
        row = db.execute(
            "SELECT * FROM usuarios WHERE id_usuario=?", (id_usuario,)
        ).fetchone()
        return _usuario(row)

def listar_clientes(busqueda=""):
    termino = f"%{busqueda.strip()}%"
    with obtener_conexion() as db:
        rows = db.execute(
            """SELECT * FROM clientes
               WHERE nombre LIKE ? OR cedula_ruc LIKE ? OR correo LIKE ?
                  OR telefono LIKE ?
               ORDER BY id_cliente DESC""",
            (termino, termino, termino, termino)
        ).fetchall()
        return [dict(r) for r in rows]

def crear_cliente(datos, responsable):
    limpio = validar_cliente(datos)
    with obtener_conexion() as db:
        if db.execute("SELECT 1 FROM clientes WHERE cedula_ruc=?",
                      (limpio["cedula_ruc"],)).fetchone():
            raise ErrorValidacion("Ya existe un cliente con esa cédula/RUC.")
        cur = db.execute(
            """INSERT INTO clientes(nombre,cedula_ruc,telefono,correo,estado)
               VALUES(?,?,?,?,?)""",
            (limpio["nombre"], limpio["cedula_ruc"], limpio["telefono"],
             limpio["correo"], limpio["estado"])
        )
        registrar_auditoria(db, "CLIENTES", "CREAR",
                            f"Cliente {limpio['nombre']} creado.", responsable)
        db.commit()
        return cur.lastrowid

def actualizar_cliente(datos, responsable):
    limpio = validar_cliente(datos, actualizacion=True)
    with obtener_conexion() as db:
        if not db.execute("SELECT 1 FROM clientes WHERE id_cliente=?",
                          (limpio["id_cliente"],)).fetchone():
            raise ErrorValidacion("El cliente seleccionado no existe.")
        dup = db.execute(
            "SELECT 1 FROM clientes WHERE cedula_ruc=? AND id_cliente<>?",
            (limpio["cedula_ruc"], limpio["id_cliente"])
        ).fetchone()
        if dup:
            raise ErrorValidacion("Ya existe otro cliente con esa cédula/RUC.")
        db.execute(
            """UPDATE clientes SET nombre=?,cedula_ruc=?,telefono=?,correo=?,estado=?
               WHERE id_cliente=?""",
            (limpio["nombre"], limpio["cedula_ruc"], limpio["telefono"],
             limpio["correo"], limpio["estado"], limpio["id_cliente"])
        )
        registrar_auditoria(db, "CLIENTES", "EDITAR",
                            f"Cliente {limpio['nombre']} actualizado.", responsable)
        db.commit()

def obtener_cliente(id_cliente):
    with obtener_conexion() as db:
        row = db.execute(
            "SELECT * FROM clientes WHERE id_cliente=?", (id_cliente,)
        ).fetchone()
        return _usuario(row)

def eliminar_cliente(id_cliente, responsable):
    with obtener_conexion() as db:
        cliente = db.execute(
            "SELECT * FROM clientes WHERE id_cliente=?", (id_cliente,)
        ).fetchone()
        if not cliente:
            raise ErrorValidacion("El cliente seleccionado no existe.")
        reserva = db.execute(
            "SELECT 1 FROM reservas WHERE id_cliente=? AND estado='Activa' LIMIT 1",
            (id_cliente,)
        ).fetchone()
        if reserva:
            raise ErrorValidacion("No se puede eliminar/inactivar: tiene reservas activas.")
        db.execute("UPDATE clientes SET estado='Inactivo' WHERE id_cliente=?", (id_cliente,))
        registrar_auditoria(db, "CLIENTES", "INACTIVAR",
                            f"Cliente {cliente['nombre']} inactivado.", responsable)
        db.commit()

def resumen():
    with obtener_conexion() as db:
        u = db.execute("SELECT COUNT(*) n FROM usuarios WHERE estado='Activo'").fetchone()["n"]
        c = db.execute("SELECT COUNT(*) n FROM clientes WHERE estado='Activo'").fetchone()["n"]
        a = db.execute("SELECT COUNT(*) n FROM usuarios WHERE rol='administrador' AND estado='Activo'").fetchone()["n"]
        return {"usuarios": u, "clientes": c, "administradores": a}
