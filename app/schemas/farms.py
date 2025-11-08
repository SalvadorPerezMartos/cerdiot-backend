# app/schemas/farms.py
from pydantic import BaseModel


class FarmBase(BaseModel):
    name: str


class FarmCreate(FarmBase):
    """Datos que se reciben al crear una granja"""
    pass


class FarmOut(FarmBase):
    id: int
    owner_user_id: int

    class Config:
        from_attributes = True  # antes orm_mode
