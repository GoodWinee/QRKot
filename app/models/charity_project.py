from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.constants import MAX_LENGTH_STRING
from app.core.db import Base, CommonMixin, InvestmentMixin


class CharityProject(CommonMixin, InvestmentMixin, Base):
    """Таблица целевых проектов."""

    __table_args__ = (
        CheckConstraint(
            'full_amount > 0',
            name='check_full_amount_positive'
        ),
        CheckConstraint(
            'invested_amount <= full_amount',
            name='check_invested_le_full'
        ),
    )

    name: Mapped[str] = mapped_column(
        String(MAX_LENGTH_STRING), unique=True, nullable=False
    )
    description: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    def __repr__(self) -> str:
        """Отладочное представление проекта."""
        return (
            f'<CharityProject {self.id} | '
            f'name={self.name!r} | '
            f'full={self.full_amount} | '
            f'invested={self.invested_amount}>'
        )
