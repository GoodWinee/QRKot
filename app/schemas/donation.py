from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer

from app.core.constants import MIN_VALUE


class DonationBase(BaseModel):
    """Базовая схема пожертвования."""

    full_amount: int = Field(gt=MIN_VALUE)
    comment: Optional[str] = None


class DonationCreate(DonationBase):
    """Создание пожертвования."""

    model_config = ConfigDict(extra='forbid')


class DonationDB(DonationBase):
    """Ответ для обычного пользователя."""
    id: int
    create_date: datetime
    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_date')
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class DonationFullInfoDB(DonationBase):
    """Полный ответ для суперпользователя."""

    id: int
    create_date: datetime
    user_id: int
    invested_amount: int
    fully_invested: bool
    close_date: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_date', 'close_date')
    def serialize_datetime(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return value.isoformat()