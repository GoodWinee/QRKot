from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (check_full_amount_valid, check_name_is_unique,
                                check_project_can_be_deleted,
                                check_project_is_open)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project as crud_project
from app.models.donation import Donation
from app.schemas.charity_project import (CharityProjectCreate,
                                         CharityProjectDB,
                                         CharityProjectUpdate)
from app.services.investment import invest

router = APIRouter()


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    tags=['charity_projects']
)
async def get_all_charity_projects(
    session: AsyncSession = Depends(get_async_session)
):
    """Список проектов. Доступно анонимным и авторизованным."""
    return await crud_project.get_multi(session)


@router.post(
    '/',
    response_model=CharityProjectDB,
    tags=['charity_projects'],
    dependencies=[Depends(current_superuser)]
)
async def create_charity_project(
    project: CharityProjectCreate,
    session: AsyncSession = Depends(get_async_session),
):
    """Создать проект. Только для суперпользователей."""
    await check_name_is_unique(project.name, session)
    db_project = await crud_project.create(project, session, commit=False)
    db_project.invested_amount = 0
    db_project.fully_invested = False
    result = await session.execute(
        select(Donation).where(Donation.fully_invested.is_(False))
    )
    open_donations = list(result.scalars().all())
    updated_donations = invest(db_project, open_donations)
    for donation in updated_donations:
        session.add(donation)
    await session.commit()
    await session.refresh(db_project)
    return db_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    tags=['charity_projects'],
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    project_: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновить проект. Только для суперпользователей."""
    project = await crud_project.get(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    check_project_is_open(project)
    if project_.name and project_.name != project.name:
        await check_name_is_unique(
            project_.name, session, exclude_id=project_id
        )
    if project_.full_amount is not None:
        check_full_amount_valid(project_.full_amount, project.invested_amount)
    updated_project = await crud_project.update(session, project, project_)
    if (
        updated_project.invested_amount >= updated_project.full_amount
        and not updated_project.fully_invested
    ):
        updated_project.fully_invested = True
        updated_project.close_date = datetime.now(timezone.utc)
        session.add(updated_project)
        await session.commit()
        await session.refresh(updated_project)
    return updated_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    tags=['charity_projects'],
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
    project_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удалить проект. Только для суперпользователей."""
    project = await crud_project.get(session, project_id)
    if not project:
        raise HTTPException(status_code=404, detail='Проект не найден!')
    check_project_can_be_deleted(project)
    return await crud_project.remove(session, project_id)
