import hashlib
import hmac
import os

ITERACIONES = 210_000

def generar_hash(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERACIONES)
    return f"pbkdf2_sha256${ITERACIONES}${salt.hex()}${digest.hex()}"

def verificar_password(password, almacenado):
    try:
        algoritmo, iters, salt_hex, digest_hex = almacenado.split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", password.encode(), bytes.fromhex(salt_hex), int(iters)
        )
        return hmac.compare_digest(calculado.hex(), digest_hex)
    except (ValueError, TypeError):
        return False
