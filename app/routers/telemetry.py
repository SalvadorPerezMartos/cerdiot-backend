from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db
from .. import models
from ..deps import get_current_user
from ..logger import logger

router = APIRouter()


# 1) ÚLTIMA telemetría por device_key
@router.get(
    "/by-device-key/{device_key}",
    summary="Último dato de telemetría de un dispositivo",
    description="Devuelve el último registro de la tabla telemetry para un device_key que sea del usuario.",
)
def get_latest_by_device_key(
    device_key: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # validar que el device es del usuario
    device = (
        db.query(models.Device)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(
            models.Device.device_key == device_key,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or not yours")

    sql = text(
        """
        SELECT id, device_key, ts_utc, temp, hum, co2, nh3
        FROM telemetry
        WHERE device_key = :dk
        ORDER BY ts_utc DESC
        LIMIT 1
        """
    )
    row = db.execute(sql, {"dk": device_key}).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="No telemetry for this device")

    logger.info("User %s got latest telemetry for %s", current_user.id, device_key)

    return {
        "id": row.id,
        "device_key": row.device_key,
        "ts_utc": row.ts_utc,
        "temp": float(row.temp) if row.temp is not None else None,
        "hum": float(row.hum) if row.hum is not None else None,
        "co2": row.co2,
        "nh3": row.nh3,
    }


# 2) HISTÓRICO por device_key, con filtros de fechas y límite
@router.get(
    "/",
    summary="Listado de telemetría",
    description=(
        "Devuelve registros de la tabla telemetry para un device_key del usuario. "
        "Puedes filtrar por from_utc / to_utc y limitar el número de registros."
    ),
)
def list_telemetry(
    device_key: str = Query(..., description="Clave del dispositivo"),
    from_utc: Optional[datetime] = Query(
        None, description="ISO8601 desde cuándo (UTC) ej: 2025-11-08T09:00:00Z"
    ),
    to_utc: Optional[datetime] = Query(
        None, description="ISO8601 hasta cuándo (UTC)"
    ),
    limit: int = Query(200, ge=1, le=2000),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # validar que el device es del usuario
    device = (
        db.query(models.Device)
        .join(models.Shed, models.Device.shed_id == models.Shed.id)
        .join(models.Farm, models.Shed.farm_id == models.Farm.id)
        .filter(
            models.Device.device_key == device_key,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or not yours")

    sql = """
        SELECT id, device_key, ts_utc, temp, hum, co2, nh3
        FROM telemetry
        WHERE device_key = :dk
    """
    params = {"dk": device_key}

    if from_utc is not None:
        sql += " AND ts_utc >= :from_utc"
        params["from_utc"] = from_utc
    if to_utc is not None:
        sql += " AND ts_utc <= :to_utc"
        params["to_utc"] = to_utc

    sql += " ORDER BY ts_utc DESC"
    sql += " LIMIT :limit"
    params["limit"] = limit

    rows = db.execute(text(sql), params).fetchall()

    logger.info(
        "User %s listed telemetry for %s -> %s rows",
        current_user.id,
        device_key,
        len(rows),
    )

    out: List[dict] = []
    for r in rows:
        out.append(
            {
                "id": r.id,
                "device_key": r.device_key,
                "ts_utc": r.ts_utc,
                "temp": float(r.temp) if r.temp is not None else None,
                "hum": float(r.hum) if r.hum is not None else None,
                "co2": r.co2,
                "nh3": r.nh3,
            }
        )
    return out
