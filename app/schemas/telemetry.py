from pydantic import BaseModel
from datetime import datetime


class TelemetryBase(BaseModel):
    device_key: str
    ts_utc: datetime
    temp: float | None = None
    hum: float | None = None
    co2: int | None = None
    nh3: int | None = None


class TelemetryOut(TelemetryBase):
    id: int

    class Config:
        from_attributes = True
