from typing import TYPE_CHECKING

from fastapi_users.db import SQLAlchemyBaseUserTable
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base

if TYPE_CHECKING:
    from app.models.donation import Donation


class User(SQLAlchemyBaseUserTable[int], Base):
    """Таблица пользователей."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    donations: Mapped[list["Donation"]] = relationship(
        back_populates="user",
        lazy="select",
        cascade="all, delete-orphan"
    )
