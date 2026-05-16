from datetime import datetime, timezone

from app.core.constants import MIN_VALUE


def invest(target, sources):
    """Распределить средства между объектами."""
    for source in sources:
        amount = min(
            target.full_amount - target.invested_amount,
            source.full_amount - source.invested_amount
        )
        if amount <= MIN_VALUE:
            continue
        target.invested_amount += amount
        source.invested_amount += amount
        if source.invested_amount >= source.full_amount:
            source.fully_invested = True
            source.close_date = datetime.now(timezone.utc)
        if target.invested_amount >= target.full_amount:
            target.fully_invested = True
            target.close_date = datetime.now(timezone.utc)
            break

    return sources
