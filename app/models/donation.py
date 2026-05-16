from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import LENGTH_COMMENT
from app.core.db import Base, CommonMixin
from app.models.user import User


class Donation(CommonMixin, Base):
    """Таблица пожертвований."""

    __tablename__ = "donation"
    comment: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, default=None
    )
    full_amount: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    close_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id"), nullable=False
    )
    user: Mapped["User"] = relationship(
        back_populates="donations", lazy="joined"
    )

    def __repr__(self) -> str:
        short_comment = self.comment[
            :LENGTH_COMMENT
        ] + "..." if self.comment and len(
            self.comment
        ) > LENGTH_COMMENT else self.comment
        return (
            f'<Donation {self.id} | '
            f'full={self.full_amount} | '
            f'invested={self.invested_amount} | '
            f'comment={short_comment!r}>'
        )
