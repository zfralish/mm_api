import enum
from pathlib import Path
from tempfile import gettempdir
from typing import Optional

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):  # noqa: WPS600
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "mm_api"
    db_pass: str = "mm_api"
    db_base: str = "mm_api"
    db_echo: bool = False

    # Variables for Redis
    redis_host: str = "mm_api-redis"
    redis_port: int = 6379
    redis_user: Optional[str] = None
    redis_pass: Optional[str] = None
    redis_base: Optional[int] = None

    # Sentry's configuration.
    sentry_dsn: Optional[str] = None
    sentry_sample_rate: float = 1.0

    # Clerk Config
    clerk_api_key: str = "clerk_api"

    # JWKS URL
    jwks_url: str = "https://api.clerk.com/v1/jwks"

    jwks: Optional[dict] = None  # type: ignore

    def __init__(self, *args, **kwargs) -> None:  # type: ignore
        super().__init__(*args, **kwargs)
        self.fetch_jwks()

    def fetch_jwks(self) -> None:
        """
        Fetch JWKS from the given URL.

        :return: JWKS dictionary.
        """
        try:
            self.jwks = httpx.get(
                self.jwks_url,
                headers={"Authorization": f"Bearer {self.clerk_api_key}"},
            ).json()
        except httpx.HTTPStatusError as e:
            print(f"HTTP error occurred: {e}")
            return
        except Exception as e:
            print(f"An error occurred: {e}")
            return

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def redis_url(self) -> URL:
        """
        Assemble REDIS URL from settings.

        :return: redis URL.
        """
        path = ""
        if self.redis_base is not None:
            path = f"/{self.redis_base}"
        return URL.build(
            scheme="redis",
            host=self.redis_host,
            port=self.redis_port,
            user=self.redis_user,
            password=self.redis_pass,
            path=path,
        )

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_prefix="MM_",
        env_file_encoding="utf-8",
    )


settings = Settings()
