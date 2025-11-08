# /opt/iot-backend/create_first_user.py
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from app.database import SessionLocal  # noqa
from app import models  # noqa
from app.security import get_password_hash  # 👉 usa el mismo que en security.py
from app.config import settings


def main():
    print(f"Usando DB: {settings.SQLALCHEMY_DATABASE_URI}")
    db = SessionLocal()

    username = "admin"
    password = "admin123"
    full_name = "Admin"

    existing = (
        db.query(models.User)
        .filter(models.User.username == username)
        .first()
    )
    if existing:
        print("User already exists, delete it first if you want to recreate it.")
        db.close()
        return

    hashed = get_password_hash(password)

    user = models.User(
        username=username,
        password_hash=hashed,
        full_name=full_name,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    print(f"User created: {user.id}")

    db.close()


if __name__ == "__main__":
    main()
