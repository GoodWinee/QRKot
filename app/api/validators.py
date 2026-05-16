from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charity_project import CharityProject


async def check_name_is_unique(
    name: str,
    session: AsyncSession,
    exclude_id: int | None = None,
) -> None:
    """Проверяет уникальность имени. Вызывает 400 при дубликате."""
    query = select(CharityProject).where(CharityProject.name == name)
    if exclude_id is not None:
        query = query.where(CharityProject.id != exclude_id)
    result = await session.execute(query)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


def check_project_is_open(project: CharityProject) -> None:
    """Проверяет статус проекта. Вызывает 400 если закрыт."""
    if project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!'
        )


def check_full_amount_valid(
    new_amount: int,
    invested_amount: int,
) -> None:
    """Проверяет сумму. Вызывает 400 если невалидно."""
    if new_amount <= 0 or new_amount < invested_amount:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                'Нелья установить значение full_amount '
                'меньше уже вложенной суммы.'
            )
        )


def check_project_can_be_deleted(project: CharityProject) -> None:
    """Проверяет удаление. Вызывает 400 если нельзя."""
    if project.invested_amount > 0 or project.fully_invested:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!'
        )
