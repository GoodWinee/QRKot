from datetime import datetime, timezone
from typing import AsyncGenerator, Optional

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)

from app.core.config import settings
from app.core.constants import MIN_VALUE


class Base(DeclarativeBase):
    """Базовый класс для моделей."""


class CommonMixin:
    """Базовый миксин с общими полями."""

    @declared_attr
    def __tablename__(cls):
        """Имя таблицы."""
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    create_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class InvestmentMixin:
    """Миксин для полей, связанных с инвестициями."""

    full_amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer, default=MIN_VALUE, nullable=False
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    close_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )


engine = create_async_engine(settings.database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator:
    """Генератор сессий."""
    async with AsyncSessionLocal() as session:
        yield session
