# /opt/iot-backend/app/models.py
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Float,
)
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)

    # activo por defecto
    is_active = Column(Boolean, nullable=False, server_default="true")

    # ahora ya tenemos flag real de admin
    is_admin = Column(Boolean, nullable=False, server_default="false")

    # un usuario puede tener varias granjas
    farms = relationship(
        "Farm",
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"


class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    owner = relationship("User", back_populates="farms")
    sheds = relationship(
        "Shed",
        back_populates="farm",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Farm id={self.id} name={self.name!r}>"


class Shed(Base):
    __tablename__ = "sheds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    farm_id = Column(
        Integer,
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
    )

    farm = relationship("Farm", back_populates="sheds")
    devices = relationship(
        "Device",
        back_populates="shed",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Shed id={self.id} name={self.name!r} farm_id={self.farm_id}>"


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_key = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    shed_id = Column(
        Integer,
        ForeignKey("sheds.id", ondelete="CASCADE"),
        nullable=False,
    )

    shed = relationship("Shed", back_populates="devices")
    telemetry = relationship(
        "Telemetry",
        back_populates="device",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} key={self.device_key!r}>"


class Telemetry(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(
        Integer,
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    ts = Column(DateTime, nullable=False, index=True)
    temp = Column(Float)
    hum = Column(Float)
    co2 = Column(Float)
    nh3 = Column(Float)

    device = relationship("Device", back_populates="telemetry")

    def __repr__(self) -> str:
        return f"<Telemetry id={self.id} device_id={self.device_id} ts={self.ts}>"
