from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # По умолчанию SQLite, чтобы проект запускался без установки PostgreSQL.
    # В Docker Compose сюда подставляется адрес PostgreSQL.
    database_url: str = "sqlite:///./booking.db"
    # Только для разработки! В реальной работе SECRET_KEY через .env или окружение.
    secret_key: str = "dev-only-secret-change-me-at-least-32-bytes"
    access_token_minutes: int = 60
    # Пользователь, который зарегистрируется с этим email, получит роль admin.
    admin_email: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
