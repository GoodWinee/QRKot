from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    app_description: str = 'Сервис для поддержки котиков'
    app_version: str = '0.1.0'
    JWT_SECRET: str = 'qrkot-secret-key-change-in-production'
    type: str = ''
    project_id: str = ''
    private_key_id: str = ''
    private_key: str = ''
    client_email: str = ''
    client_id: str = ''
    auth_uri: str = ''
    token_uri: str = ''
    auth_provider_x509_cert_url: str = ''
    client_x509_cert_url: str = ''
    email: str = ''
    model_config = {'env_file': '.env', 'extra': 'ignore'}


settings = Settings()