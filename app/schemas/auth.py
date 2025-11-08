# app/schemas/auth.py
from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: str | None = None


class UserPublic(BaseModel):
    id: int
    username: str
    full_name: str | None = None
    is_active: bool = True
    # poner default para no reventar si en BBDD hay NULL
    is_admin: bool = False

    class Config:
        from_attributes = True  # antes era orm_mode = True en Pydantic v1
