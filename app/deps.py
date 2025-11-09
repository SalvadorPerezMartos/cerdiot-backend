# app/deps.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import get_db
from . import models
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> models.User:
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
    return user


def get_farm_owned(farm_id: int, db: Session, current_user: models.User) -> models.Farm:
    farm = (
        db.query(models.Farm)
        .filter(
            models.Farm.id == farm_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return farm


def get_shed_owned(shed_id: int, db: Session, current_user: models.User) -> models.Shed:
    shed = (
        db.query(models.Shed)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(
            models.Shed.id == shed_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not shed:
        raise HTTPException(status_code=404, detail="Shed not found")
    return shed


def get_device_owned(device_id: int, db: Session, current_user: models.User) -> models.Device:
    device = (
        db.query(models.Device)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(
            models.Device.id == device_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device
