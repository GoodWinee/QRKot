import time
from typing import AsyncGenerator

import jwt
import requests

from app.core.config import settings
from app.core.constants import GOOGLE_API_SCOPE_BASE

SCOPES = [
    f'{GOOGLE_API_SCOPE_BASE}/spreadsheets',
    f'{GOOGLE_API_SCOPE_BASE}/drive'
]

INFO = {
    "type": settings.type,
    "project_id": settings.project_id,
    "private_key_id": settings.private_key_id,
    "private_key": settings.private_key.replace('\\n', '\n'),
    "client_email": settings.client_email,
    "client_id": settings.client_id,
    "auth_uri": settings.auth_uri,
    "token_uri": settings.token_uri,
    "auth_provider_x509_cert_url": settings.auth_provider_x509_cert_url,
    "client_x509_cert_url": settings.client_x509_cert_url,
}


def _get_access_token() -> str:
    """Получить access token для Google API (без кеша)."""
    now = int(time.time())
    payload = {
        'iss': INFO['client_email'],
        'scope': ' '.join(SCOPES),
        'aud': INFO['token_uri'],
        'exp': now + 3600,
        'iat': now,
    }

    assertion = jwt.encode(
        payload,
        INFO['private_key'],
        algorithm='RS256',
        headers={'kid': INFO['private_key_id']}
    )

    response = requests.post(
        INFO['token_uri'],
        data={
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
            'assertion': assertion
        }
    )
    response.raise_for_status()
    return response.json()['access_token']


async def get_service(
    api_name: str = 'sheets',
    api_version: str = 'v4'
) -> AsyncGenerator:
    """Возвращает сервис для работы с Google API как асинхронный генератор."""
    token = _get_access_token()

    if api_name == 'sheets':
        yield _GoogleSheetsService(token)
    elif api_name == 'drive':
        yield _GoogleDriveService(token)
    else:
        raise ValueError(f"Unknown API: {api_name}")


class _GoogleSheetsService:
    """Внутренний сервис для Google Sheets API."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://sheets.googleapis.com/v4/spreadsheets'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def spreadsheets(self):
        return self

    def create(self, body: dict) -> dict:
        """Создать новую таблицу."""
        response = requests.post(
            'https://sheets.googleapis.com/v4/spreadsheets',
            headers=self.headers,
            json=body
        )
        response.raise_for_status()
        return response.json()

    def values(self):
        return self

    def update(
        self,
        spreadsheetId: str,
        range: str,
        valueInputOption: str,
        body: dict
    ) -> dict:
        """Обновить значения в таблице."""
        url = f'{self.base_url}/{spreadsheetId}/values/{range}'
        params = {'valueInputOption': valueInputOption}
        response = requests.put(
            url, headers=self.headers, params=params, json=body
        )
        response.raise_for_status()
        return response.json()


class _GoogleDriveService:
    """Внутренний сервис для Google Drive API."""

    def __init__(self, token: str):
        self.token = token
        self.base_url = 'https://www.googleapis.com/drive/v3'
        self.headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def permissions(self):
        return self

    def create(self, fileId: str, body: dict, fields: str) -> dict:
        """Создать разрешение на файл."""
        url = f'{self.base_url}/files/{fileId}/permissions'
        params = {'fields': fields}
        response = requests.post(
            url, headers=self.headers, params=params, json=body
        )
        response.raise_for_status()
        return response.json()
