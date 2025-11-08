# app/routers/auth.py
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app import models
from app.security import (
    verify_password,
    create_access_token,
    get_password_hash,
)
from app.deps import get_current_user
from app.schemas.auth import UserPublic  # debe tener is_admin si lo quieres devolver

router = APIRouter()


# ====== SCHEMAS ======
class UserRegister(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    # lo añadimos para que un admin pueda crear otro admin
    is_admin: bool = False


# ====== ENDPOINTS ======

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = (
        db.query(models.User)
        .filter(models.User.username == form_data.username)
        .first()
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_access_token({"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserPublic)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserPublic, status_code=201)
def register_user(
    user_in: UserRegister,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Crea un nuevo usuario.
    Ahora validamos por flag de BBDD (is_admin) en vez de por username="admin"
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users",
        )

    # comprobar si ya existe
    existing = (
        db.query(models.User)
        .filter(models.User.username == user_in.username)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    user = models.User(
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        full_name=user_in.full_name or user_in.username,
        is_active=user_in.is_active,
        is_admin=user_in.is_admin,  # nuevo
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
