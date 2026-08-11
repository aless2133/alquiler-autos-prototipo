from dataclasses import dataclass
from typing import Optional

@dataclass
class UsuarioInterno:
    id_usuario: Optional[int]
    nombre: str
    username: str
    rol: str
    estado: str
    fecha_registro: Optional[str] = None

@dataclass
class Cliente:
    id_cliente: Optional[int]
    nombre: str
    cedula_ruc: str
    telefono: str
    correo: str
    estado: str
    fecha_registro: Optional[str] = None
