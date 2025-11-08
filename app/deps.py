# /opt/iot-backend/app/deps.py
from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from . import models
from .security import decode_access_token

# el login está en /auth/login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
    """
    Lee el JWT, saca el user_id (viene en "sub") y carga el usuario.
    """
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user_id = int(payload["sub"])
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    return user


# ================== HELPERS DE DUEÑO ==================

def get_farm_owned(
    farm_id: int,
    db: Session,
    current_user: models.User,
) -> models.Farm:
    # los admins pueden ver todo
    q = db.query(models.Farm).filter(models.Farm.id == farm_id)
    if not current_user.is_admin:
        q = q.filter(models.Farm.owner_user_id == current_user.id)

    farm = q.first()
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


def get_shed_owned(
    shed_id: int,
    db: Session,
    current_user: models.User,
) -> models.Shed:
    q = (
        db.query(models.Shed)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(models.Shed.id == shed_id)
    )
    if not current_user.is_admin:
        q = q.filter(models.Farm.owner_user_id == current_user.id)

    shed = q.first()
    if not shed:
        raise HTTPException(status_code=404, detail="Shed not found")
    return shed


def get_device_owned(
    device_id: int,
    db: Session,
    current_user: models.User,
) -> models.Device:
    q = (
        db.query(models.Device)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(models.Device.id == device_id)
    )
    if not current_user.is_admin:
        q = q.filter(models.Farm.owner_user_id == current_user.id)

    device = q.first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
