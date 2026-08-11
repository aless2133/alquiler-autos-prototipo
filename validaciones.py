import re

ROLES = ("administrador", "empleado")
ESTADOS = ("Activo", "Inactivo")

class ErrorValidacion(ValueError):
    pass

def limpiar_texto(valor):
    return " ".join((valor or "").strip().split())

def validar_correo(correo):
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo or ""):
        raise ErrorValidacion("El correo electrónico no tiene un formato válido.")

def validar_cedula_ruc(valor):
    valor = limpiar_texto(valor)
    if not re.fullmatch(r"\d{10}|\d{13}", valor):
        raise ErrorValidacion("La cédula debe tener 10 dígitos o el RUC 13 dígitos.")

def validar_telefono(valor):
    if not re.fullmatch(r"\d{7,10}", limpiar_texto(valor)):
        raise ErrorValidacion("El teléfono debe tener entre 7 y 10 dígitos.")

def validar_cliente(datos, actualizacion=False):
    nombre = limpiar_texto(datos.get("nombre"))
    cedula = limpiar_texto(datos.get("cedula_ruc"))
    telefono = limpiar_texto(datos.get("telefono"))
    correo = limpiar_texto(datos.get("correo"))
    estado = limpiar_texto(datos.get("estado", "Activo"))
    if not nombre:
        raise ErrorValidacion("El nombre del cliente es obligatorio.")
    validar_cedula_ruc(cedula)
    validar_telefono(telefono)
    validar_correo(correo)
    if estado not in ESTADOS:
        raise ErrorValidacion("Seleccione un estado válido.")
    limpio = {"nombre": nombre, "cedula_ruc": cedula, "telefono": telefono,
              "correo": correo, "estado": estado}
    if actualizacion:
        limpio["id_cliente"] = int(datos["id_cliente"])
    return limpio

def validar_usuario_interno(datos, actualizacion=False):
    nombre = limpiar_texto(datos.get("nombre"))
    username = limpiar_texto(datos.get("username"))
    rol = limpiar_texto(datos.get("rol"))
    estado = limpiar_texto(datos.get("estado", "Activo"))
    password = datos.get("password", "")
    if not nombre:
        raise ErrorValidacion("El nombre es obligatorio.")
    if not username or len(username) < 4:
        raise ErrorValidacion("El usuario debe tener al menos 4 caracteres.")
    if rol not in ROLES:
        raise ErrorValidacion("Seleccione un rol válido.")
    if estado not in ESTADOS:
        raise ErrorValidacion("Seleccione un estado válido.")
    if not actualizacion and len(password) < 8:
        raise ErrorValidacion("La contraseña debe tener al menos 8 caracteres.")
    limpio = {"nombre": nombre, "username": username, "rol": rol, "estado": estado,
              "password": password}
    if actualizacion:
        if "id_usuario" not in datos:
            raise ErrorValidacion("Falta identificar el usuario a actualizar.")
        limpio["id_usuario"] = int(datos["id_usuario"])
    return limpio

def validar_credenciales(username, password):
    if not limpiar_texto(username) or not password:
        raise ErrorValidacion("Ingrese usuario y contraseña.")
