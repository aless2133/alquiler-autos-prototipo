from pathlib import Path
import sqlite3
from seguridad import generar_hash

RUTA_DB = Path(__file__).resolve().parent / "sprint1.db"

def obtener_conexion():
    conexion = sqlite3.connect(RUTA_DB)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion

def inicializar_base_datos():
    with obtener_conexion() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            rol TEXT NOT NULL CHECK (rol IN ('administrador','empleado')),
            estado TEXT NOT NULL DEFAULT 'Activo'
                CHECK (estado IN ('Activo','Inactivo')),
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS clientes (
            id_cliente INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cedula_ruc TEXT NOT NULL UNIQUE,
            telefono TEXT NOT NULL,
            correo TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Activo'
                CHECK (estado IN ('Activo','Inactivo')),
            fecha_registro TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS reservas (
            id_reserva INTEGER PRIMARY KEY AUTOINCREMENT,
            id_cliente INTEGER NOT NULL,
            estado TEXT NOT NULL DEFAULT 'Activa',
            FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
        );
        CREATE TABLE IF NOT EXISTS intentos_login (
            username TEXT PRIMARY KEY,
            intentos INTEGER NOT NULL DEFAULT 0,
            bloqueado_hasta REAL NOT NULL DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modulo TEXT NOT NULL,
            accion TEXT NOT NULL,
            detalle TEXT NOT NULL,
            responsable TEXT,
            fecha TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        existe = db.execute("SELECT COUNT(*) AS n FROM usuarios").fetchone()["n"]
        if not existe:
            db.execute(
                """INSERT INTO usuarios(nombre, username, password_hash, rol)
                   VALUES (?, ?, ?, 'administrador')""",
                ("Administrador principal", "admin", generar_hash("Admin123!"))
            )

def registrar_auditoria(db, modulo, accion, detalle, responsable):
    db.execute(
        "INSERT INTO auditoria(modulo, accion, detalle, responsable) VALUES (?,?,?,?)",
        (modulo, accion, detalle, responsable)
    )
