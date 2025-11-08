# app/routers/devices.py

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import get_db
from app import models
from app.deps import get_current_user
from app.logger import logger
from app.schemas.devices import (
    DeviceCreate,
    DeviceOut,
    DeviceWithLatestOut,
)

router = APIRouter(
    tags=["devices"]
)
# ojo: en app.main ya haces:
# app.include_router(devices.router, prefix="/devices", tags=["devices"])
# así que aquí no hace falta poner prefix


@router.post(
    "/",
    response_model=DeviceOut,
    summary="Registrar un dispositivo",
    description="Crea un dispositivo en una nave del usuario. El device_key debe ser único.",
)
def create_device(
    device_in: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 1) comprobar que el shed pertenece a una granja del usuario
    shed = (
        db.query(models.Shed)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(
            models.Shed.id == device_in.shed_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not shed:
        logger.warning(
            f"User {current_user.id} tried to create device in shed {device_in.shed_id} not owned"
        )
        raise HTTPException(status_code=404, detail="Shed not found or not yours")

    # 2) comprobar que no exista ya el device_key
    existing = (
        db.query(models.Device)
        .filter(models.Device.device_key == device_in.device_key)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Device key already exists")

    device = models.Device(
        device_key=device_in.device_key,
        shed_id=device_in.shed_id,
        description=device_in.description,
    )
    db.add(device)
    db.commit()
    db.refresh(device)

    logger.info(
        f"User {current_user.id} created device id={device.id} key={device.device_key}"
    )
    return device


@router.get(
    "/",
    response_model=list[DeviceOut],
    summary="Listar mis dispositivos",
    description="Devuelve los dispositivos de todas las granjas del usuario autenticado. Soporta paginación.",
)
def list_devices(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    devices = (
        db.query(models.Device)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(models.Farm.owner_user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.info(
        f"User {current_user.id} listed devices skip={skip} limit={limit} -> {len(devices)} results"
    )
    return devices


@router.get(
    "/with-latest",
    response_model=list[DeviceWithLatestOut],
    summary="Listar dispositivos con última telemetría",
    description="Devuelve los dispositivos del usuario junto con la última fila de la tabla telemetry para cada uno.",
)
def list_devices_with_latest(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # 1) sacar todos los devices del usuario
    rows = (
        db.query(models.Device, models.Shed, models.Farm)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(models.Farm.owner_user_id == current_user.id)
        .all()
    )

    result: list[DeviceWithLatestOut] = []

    for device, shed, farm in rows:
        # 2) última telemetría de este device_key
        sql = text(
            """
            SELECT device_key, ts_utc, temp, hum, co2, nh3
            FROM telemetry
            WHERE device_key = :dk
            ORDER BY ts_utc DESC
            LIMIT 1
            """
        )
        latest_row = db.execute(sql, {"dk": device.device_key}).fetchone()

        if latest_row:
            latest = {
                "ts_utc": latest_row.ts_utc,
                "temp": latest_row.temp,
                "hum": latest_row.hum,
                "co2": latest_row.co2,
                "nh3": latest_row.nh3,
            }
        else:
            latest = None

        result.append(
            DeviceWithLatestOut(
                id=device.id,
                device_key=device.device_key,
                description=device.description,
                shed_id=device.shed_id,
                shed_name=shed.name,
                farm_id=farm.id,
                farm_name=farm.name,
                latest=latest,
            )
        )

    logger.info(
        f"User {current_user.id} listed devices with latest -> {len(result)} results"
    )
    return result
