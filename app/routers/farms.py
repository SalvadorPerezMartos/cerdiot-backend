# app/routers/farms.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.deps import get_current_user
from app.logger import logger
from app.schemas.farms import FarmCreate, FarmOut
from app.schemas.sheds import ShedOut  # para el endpoint de sheds

router = APIRouter()


@router.get(
    "/",
    response_model=list[FarmOut],
    summary="Listar las granjas del usuario autenticado",
    description=(
        "Devuelve todas las granjas registradas cuyo `owner_user_id` coincide con el del usuario autenticado. "
        "Permite paginación mediante los parámetros `skip` y `limit`."
    ),
)
def list_my_farms(
    skip: int = Query(0, ge=0, description="Número de registros a omitir (paginación)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo número de resultados devueltos"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lista las granjas del usuario autenticado."""
    farms = (
        db.query(models.Farm)
        .filter(models.Farm.owner_user_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info(
        "User %s listed farms skip=%s limit=%s -> %s results",
        current_user.id,
        skip,
        limit,
        len(farms),
    )
    return farms


@router.post(
    "/",
    response_model=FarmOut,
    summary="Crear una nueva granja",
    description=(
        "Crea una nueva granja en la base de datos y la asocia al usuario autenticado. "
        "El campo `name` es obligatorio."
    ),
)
def create_farm(
    farm_in: FarmCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Crea una granja para el usuario autenticado."""
    farm = models.Farm(
        name=farm_in.name,
        owner_user_id=current_user.id,
    )
    db.add(farm)
    db.commit()
    db.refresh(farm)

    logger.info("User %s created farm id=%s", current_user.id, farm.id)
    return farm


@router.get(
    "/{farm_id}/sheds",
    response_model=list[ShedOut],
    summary="Listar las naves de una granja",
    description=(
        "Devuelve las naves pertenecientes a una granja propiedad del usuario autenticado. "
        "Lanza un error 404 si la granja no pertenece al usuario o no existe."
    ),
)
def list_sheds_of_farm(
    farm_id: int,
    skip: int = Query(0, ge=0, description="Número de registros a omitir (paginación)"),
    limit: int = Query(100, ge=1, le=500, description="Máximo número de resultados devueltos"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """Lista las naves de una granja propiedad del usuario."""
    farm = (
        db.query(models.Farm)
        .filter(
            models.Farm.id == farm_id,
            models.Farm.owner_user_id == current_user.id,
        )
        .first()
    )
    if not farm:
        logger.warning(
            "User %s tried to list sheds of farm %s that is not his",
            current_user.id,
            farm_id,
        )
        raise HTTPException(status_code=404, detail="Farm not found")

    sheds = (
        db.query(models.Shed)
        .filter(models.Shed.farm_id == farm_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.info(
        "User %s listed sheds of farm %s skip=%s limit=%s -> %s results",
        current_user.id,
        farm_id,
        skip,
        limit,
        len(sheds),
    )
    return sheds
