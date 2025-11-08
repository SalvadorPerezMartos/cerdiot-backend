from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List

from ..database import get_db
from .. import models
from ..deps import get_current_user
from ..logger import logger

router = APIRouter(
    prefix="/sheds",
    tags=["sheds"],
)


# ---------- SCHEMAS ----------
class ShedBase(BaseModel):
    name: str


class ShedCreate(ShedBase):
    farm_id: int


class ShedOut(ShedBase):
    id: int
    farm_id: int

    class Config:
        from_attributes = True


# ---------- ENDPOINTS ---------
@router.post(
    "/",
    response_model=ShedOut,
    summary="Crear una nave",
    description="Crea una nave dentro de una granja que pertenezca al usuario autenticado.",
)
def create_shed(
    shed_in: ShedCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # comprobar que la granja es del usuario
    farm = (
        db.query(models.Farm)
        .filter(
            models.Farm.id == shed_in.farm_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not farm:
        logger.warning(f"User {current_user.id} tried to create shed in farm {shed_in.farm_id} not owned")
        raise HTTPException(status_code=404, detail="Farm not found")

    shed = models.Shed(
        name=shed_in.name,
        farm_id=shed_in.farm_id,
    )
    db.add(shed)
    db.commit()
    db.refresh(shed)
    logger.info(f"User {current_user.id} created shed id={shed.id} in farm {shed_in.farm_id}")
    return shed


@router.get(
    "/{shed_id}",
    response_model=ShedOut,
    summary="Obtener una nave",
    description="Devuelve una nave siempre que pertenezca a alguna granja del usuario autenticado.",
)
def get_shed(
    shed_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
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
        logger.warning(f"User {current_user.id} tried to get shed {shed_id} not owned")
        raise HTTPException(status_code=404, detail="Shed not found")
    return shed
