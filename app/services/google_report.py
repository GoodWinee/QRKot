from datetime import datetime
from typing import Any

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.google_client import get_service
from app.models.charity_project import CharityProject


async def get_projects_by_completion_rate(
    session: AsyncSession
) -> list[CharityProject]:
    """Получить закрытые проекты, отсортированные по скорости сбора средств."""
    result = await session.execute(
        CharityProject.__table__.select()
        .where(CharityProject.fully_invested.is_(True))
        .order_by(
            func.julianday(CharityProject.close_date) -
            func.julianday(CharityProject.create_date)
        )
    )
    projects = []
    for row in result.fetchall():
        project = CharityProject(
            id=row.id,
            name=row.name,
            description=row.description,
            full_amount=row.full_amount,
            invested_amount=row.invested_amount,
            fully_invested=row.fully_invested,
            create_date=row.create_date,
            close_date=row.close_date,
        )
        projects.append(project)
    return projects


def create_spreadsheets(service: Any, name: str) -> str:
    """Создать новую Google Таблицу. Возвращает ID."""
    spreadsheet = {'properties': {'title': name}}
    result = service.spreadsheets().create(body=spreadsheet)
    return result.get('spreadsheetId')


def set_user_permissions(service: Any, spreadsheet_id: str) -> None:
    """Предоставить права на редактирование таблицы личному аккаунту."""
    permissions = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email,
    }
    service.permissions().create(
        fileId=spreadsheet_id,
        body=permissions,
        fields='id'
    )


def update_spreadsheets_value(
    service: Any,
    spreadsheet_id: str,
    values: list[list[Any]],
    range_name: str = 'A1:C100'
) -> None:
    """Обновить данные в Google Таблице."""
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    )


async def generate_report(session: AsyncSession) -> dict[str, Any]:
    """Сгенерировать отчёт в Google Таблице. Возвращает ссылку на таблицу."""
    projects = await get_projects_by_completion_rate(session)
    async for sheets_service in get_service('sheets', 'v4'):
        async for drive_service in get_service('drive', 'v3'):
            spreadsheet_id = create_spreadsheets(
                sheets_service,
                f'Отчёт от {datetime.now().strftime("%Y/%m/%d %H:%M:%S")}'
            )
            set_user_permissions(drive_service, spreadsheet_id)
            report_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            values = [
                ['Отчёт от', report_time],
                ['Топ проектов по скорости закрытия'],
                ['Название проекта', 'Время сбора', 'Описание'],
            ]
            project_rows = [
                [
                    project.name,
                    str(project.close_date - project.create_date),
                    project.description,
                ]
                for project in projects
            ]
            values.extend(project_rows)
            update_spreadsheets_value(sheets_service, spreadsheet_id, values)
            return {
                'spreadsheet_id': spreadsheet_id,
                'url': f'https://docs.google.com/spreadsheets/d/{
                    spreadsheet_id
                }'
            }
    return {'error': 'Failed to create report'}
