from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import MIN_VALUE
from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import donation as crud_donation
from app.models.charity_project import CharityProject
from app.models.user import User
from app.schemas.donation import DonationCreate, DonationDB, DonationFullInfoDB
from app.services.investment import invest

router = APIRouter()


@router.get(
    '/',
    response_model=list[DonationFullInfoDB],
    tags=['donations'],
    dependencies=[Depends(current_superuser)]
)
async def get_all_donations(
    session: AsyncSession = Depends(get_async_session),
    _: User = Depends(current_superuser)
):
    """Список всех пожертвований. Только для суперпользователей."""
    return await crud_donation.get_multi(session)


@router.get(
    '/my',
    response_model=list[DonationDB],
    tags=['donations']
)
async def get_my_donations(
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user)
):
    """Список пожертвований текущего пользователя."""
    result = await session.execute(
        select(crud_donation.model).where(
            crud_donation.model.user_id == user.id
        )
    )
    return list(result.scalars().all())


@router.post(
    '/',
    response_model=DonationDB,
    response_model_exclude_none=True,
    tags=['donations']
)
async def create_donation(
    donation_in: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    """Создать пожертвование. Только для авторизованных."""
    db_donation = await crud_donation.create(
        donation_in, session, commit=False
    )
    db_donation.user_id = user.id
    db_donation.invested_amount = MIN_VALUE
    db_donation.fully_invested = False
    result_projects = await session.execute(
        select(CharityProject).where(CharityProject.fully_invested.is_(False))
    )
    open_projects = list(result_projects.scalars().all())
    updated_projects = invest(db_donation, open_projects)
    for project in updated_projects:
        session.add(project)
    await session.commit()
    await session.refresh(db_donation)
    response_data = {
        'full_amount': db_donation.full_amount,
        'id': db_donation.id,
        'create_date': db_donation.create_date.isoformat(),
    }
    if db_donation.comment is not None:
        response_data['comment'] = db_donation.comment
    return response_data
