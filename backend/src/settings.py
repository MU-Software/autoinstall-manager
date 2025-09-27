from __future__ import annotations

from functools import cached_property
from pathlib import Path
from typing import ClassVar, cast

from fastapi.openapi.models import Contact, License
from packaging.version import InvalidVersion, Version
from pydantic import DirectoryPath, HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio.engine import AsyncEngine, async_engine_from_config
from sqlalchemy.ext.asyncio.session import AsyncSession, async_sessionmaker
from toml import load as toml_load
from uvicorn.config import Config


class ServerSetting(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    root_path: DirectoryPath


class SQLAlchemySetting(BaseSettings):
    driver: str
    host: str
    port: int
    username: str
    password: str
    name: str

    echo: bool = False
    echo_pool: bool = False
    pool_pre_ping: bool = True
    autoflush: bool = True
    expire_on_commit: bool = False
    connect_timeout: float = 15.0

    model_config = SettingsConfigDict(validate_default=True)

    ENGINE_CONFIG_FIELDS: ClassVar[set[str]] = {"echo", "echo_pool", "pool_pre_ping"}
    SESSION_MAKER_CONFIG_FIELDS: ClassVar[set[str]] = {"autoflush", "expire_on_commit"}

    @cached_property
    def url(self) -> str:
        return str(
            PostgresDsn.build(
                scheme=f"postgresql+{self.driver}",
                username=self.username,
                password=self.password,
                host=self.host,
                port=self.port,
                path=self.name,
            )
        )

    @cached_property
    def engine(self) -> AsyncEngine:
        config = self.model_dump(include=self.ENGINE_CONFIG_FIELDS) | {"url": self.url}
        return async_engine_from_config(prefix="", configuration=config)

    @cached_property
    def session_maker(self) -> async_sessionmaker[AsyncSession]:
        config = self.model_dump(include=self.SESSION_MAKER_CONFIG_FIELDS)
        return async_sessionmaker(**config, bind=self.engine, class_=AsyncSession)

    async def cleanup(self) -> None:
        del self.session_maker

        if self.engine:
            await self.engine.dispose()

        del self.engine


class ProjectInfoSetting(BaseSettings):
    title: str
    description: str
    version: str
    summary: str | None = None
    terms_of_service: HttpUrl | None = None
    contact: Contact | None = None
    license: License | None = None

    @field_validator("version", mode="before")
    @classmethod
    def validate_version(cls, v: str) -> str:
        try:
            return str(Version(v))
        except InvalidVersion as err:
            raise ValueError(f"Invalid version: {v}") from err

    @classmethod
    def from_pyproject(cls) -> ProjectInfoSetting:
        project_info: dict = toml_load(Path.cwd() / "pyproject.toml")["project"]

        contact: Contact | None = None
        if authors := cast(list[dict[str, str]], project_info.get("authors", None)):
            contact = Contact.model_validate(authors[0] | {"url": project_info.get("homepage", None)})

        return ProjectInfoSetting(
            title=project_info["name"],
            description=project_info["description"],
            version=project_info["version"],
            contact=contact,
        )


class OpenAPISetting(BaseSettings):
    # OpenAPI related configs
    # Only available when debug mode is enabled
    docs_url: str | None = "/docs"
    redoc_url: str | None = "/redoc"
    openapi_url: str | None = "/openapi.json"
    openapi_prefix: str | None = ""

    @classmethod
    def blank(cls) -> OpenAPISetting:
        return cls(docs_url=None, redoc_url=None, openapi_url=None, openapi_prefix=None)


class ProjectSetting(BaseSettings):
    sqlalchemy: SQLAlchemySetting
    server: ServerSetting

    openapi: OpenAPISetting = OpenAPISetting()
    project_info: ProjectInfoSetting = ProjectInfoSetting.from_pyproject()

    @classmethod
    def from_dotenv(cls, env_file: str = ".env") -> ProjectSetting:
        if not Path(env_file).is_file():
            return ProjectSetting()

        return ProjectSetting(
            _env_file=env_file,
            _env_file_encoding="utf-8",
            _env_nested_delimiter="__",
            _case_sensitive=False,
        )

    def to_fastapi_config(self) -> dict:
        # See fastapi.FastAPI.__init__ keyword arguments for more details
        project_config: dict = self.project_info.model_dump()
        openapi_config: dict = (self.openapi if self.server.debug else OpenAPISetting.blank()).model_dump()
        server_config: dict = self.server.model_dump(mode="json", include={"root_path", "debug"})

        return project_config | openapi_config | server_config

    def to_uvicorn_config(self) -> Config:
        return Config(
            app="src:create_app",
            factory=True,
            host=self.server.host,
            port=self.server.port,
            reload=self.server.debug,
        )
