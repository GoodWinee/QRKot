"""Схемы для проектов."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class CharityProjectBase(BaseModel):
    """Базовая схема проекта."""

    name: str = Field(min_length=5, max_length=100)
    description: str = Field(min_length=10)
    full_amount: int = Field(gt=0)


class CharityProjectCreate(CharityProjectBase):
    """Схема для создания проекта."""

    model_config = ConfigDict(extra='forbid')


class CharityProjectUpdate(BaseModel):
    """Схема для обновления проекта."""

    name: Optional[str] = Field(None, min_length=5, max_length=100)
    description: Optional[str] = Field(None, min_length=10)
    full_amount: Optional[int] = Field(None, gt=0)
    model_config = ConfigDict(extra='forbid')


class CharityProjectDB(CharityProjectBase):
    """Схема ответа для проектов."""

    id: int
    invested_amount: int
    fully_invested: bool
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_date', 'close_date')
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()
