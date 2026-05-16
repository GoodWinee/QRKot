from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """Схема чтения пользователя."""


class UserCreate(schemas.BaseUserCreate):
    """Схема создания пользователя."""


class UserUpdate(schemas.BaseUserUpdate):
    """Схема обновления пользователя."""
