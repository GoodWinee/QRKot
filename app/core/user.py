from typing import AsyncGenerator

from fastapi import Depends, Request
from fastapi_users import (BaseUserManager, FastAPIUsers, IntegerIDMixin,
                           exceptions)
from fastapi_users.authentication import (AuthenticationBackend,
                                          BearerTransport, JWTStrategy)
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.constants import MIN_LENGTH_PASSWORD
from app.core.db import get_async_session
from app.core.decorators import doc
from app.models.user import User
from app.schemas.user import UserCreate

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.JWT_SECRET, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """Менеджер пользователей."""

    reset_password_token_secret = settings.JWT_SECRET
    verification_token_secret = settings.JWT_SECRET

    @doc(f"Валидация пароля: минимум {MIN_LENGTH_PASSWORD} символа.")
    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        if len(password) < MIN_LENGTH_PASSWORD:
            raise exceptions.InvalidPasswordException(
                reason=(
                    f"Password should be at least {MIN_LENGTH_PASSWORD}"
                    "characters"
                )
            )
        await super().validate_password(password, user)

    async def on_after_register(
        self, user: User, request: Request | None = None
    ):
        pass


async def get_user_manager(
    session: AsyncSession = Depends(get_async_session)
) -> AsyncGenerator[UserManager, None]:
    """Создаёт и возвращает менеджер пользователей."""
    yield UserManager(SQLAlchemyUserDatabase(session, User))

fastapi_users = FastAPIUsers[User, int](get_user_manager, [auth_backend])


current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
