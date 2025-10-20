from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, CliSettingsSource, PydanticBaseSettingsSource, SettingsConfigDict


class Settings(BaseSettings):
    name: str = Field("Open Markets Server")
    environment: str = Field("development")
    transport: str = Field("stdio")
    host: str = Field("127.0.0.1")
    port: int = Field(8000)
    debug: bool = Field(False)
    timeout: float = Field(5.0)
    cors_allow_origins: str = Field("*")
    tools_module: str = Field("openmarkets.tools")

    model_config = SettingsConfigDict(env_file=".env")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            CliSettingsSource(settings_cls, cli_parse_args=True, cli_ignore_unknown_args=True),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
