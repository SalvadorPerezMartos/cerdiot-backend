# /opt/iot-backend/app/security.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# ✅ usamos pbkdf2_sha256 en lugar de bcrypt (más portable)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


# --------- PASSWORDS ----------
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# --------- TOKENS ----------
def create_access_token(data: dict, expires_minutes: Optional[int] = None) -> str:
    """
    Crea un JWT firmado con la clave secreta definida en settings.
    """
    to_encode = data.copy()

    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_minutes

    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Devuelve el payload del token si es válido; None si no lo es.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError:
        return None
