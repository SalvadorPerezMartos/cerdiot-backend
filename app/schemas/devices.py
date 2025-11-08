# app/schemas/devices.py

from datetime import datetime
from pydantic import BaseModel
from typing import Optional


# -------- bases --------
class DeviceBase(BaseModel):
    device_key: str
    description: Optional[str] = None
    shed_id: int


class DeviceCreate(BaseModel):
    device_key: str
    shed_id: int
    description: Optional[str] = None


class DeviceOut(DeviceBase):
    id: int

    class Config:
        from_attributes = True  # equivale al antiguo orm_mode = True


# ------- mini telemetría para /devices/with-latest -------
class TelemetryMini(BaseModel):
    ts_utc: datetime
    temp: Optional[float] = None
    hum: Optional[float] = None
    co2: Optional[int] = None
    nh3: Optional[int] = None


class DeviceWithLatestOut(BaseModel):
    id: int
    device_key: str
    description: Optional[str] = None

    # info de jerarquía
    shed_id: int
    shed_name: str
    farm_id: int
    farm_name: str

    # última telemetría (o None si no hay)
    latest: Optional[TelemetryMini] = None
