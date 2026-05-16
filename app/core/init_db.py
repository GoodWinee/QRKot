from fastapi_users.password import PasswordHelper
from sqlalchemy import select

from app.core.db import AsyncSessionLocal
from app.models.user import User


async def create_user(
    email: str,
    password: str,
    is_superuser: bool = False,
) -> User:
    """Создает пользователя в базе данных."""
    pwd_helper = PasswordHelper()
    hashed_password = pwd_helper.hash(password)

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.email == email))
        existing_user = result.scalar_one_or_none()
        if existing_user:
            print(f"✅ User {email} already exists.")
            return existing_user

        new_user = User(
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_superuser=is_superuser,
            is_verified=True,
        )
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        print(f"✅ User {email} created successfully.")
        return new_user
