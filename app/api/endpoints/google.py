from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.services.google_report import generate_report

router = APIRouter(prefix='/google', tags=['Google'])


@router.get('/generate_report')
async def get_report(
    session: AsyncSession = Depends(get_async_session)
):
    """Сгенерировать отчёт в Google Таблице."""
    try:
        return await generate_report(session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f'Ошибка при создании отчёта: {str(e)}'
        )
