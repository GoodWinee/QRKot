from typing import Generic, Type, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel | None)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Базовый класс для CRUD операций."""

    def __init__(self, model: Type[ModelType]):
        """Инициализация с моделью."""
        self.model = model

    async def get(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> ModelType | None:
        """Получить объект по ID."""
        result = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return result.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
    ) -> list[ModelType]:
        """Получить все объекты."""
        result = await session.execute(select(self.model))
        return list(result.scalars().all())

    async def create(
        self,
        obj_in: CreateSchemaType,
        session: AsyncSession,
        commit: bool = True,
    ) -> ModelType:
        """Создать новый объект."""
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        if commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Обновить объект."""
        if obj_in is None:
            await session.commit()
            await session.refresh(db_obj)
            return db_obj
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def remove(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> ModelType | None:
        """Удалить объект."""
        obj = await self.get(session, obj_id)
        if not obj:
            return None
        await session.delete(obj)
        await session.commit()
        return obj
