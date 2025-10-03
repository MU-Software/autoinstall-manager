from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from os import getenv

from fastapi import FastAPI
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware

from .error_handlers import get_error_handlers
from .routes import router
from .settings import ProjectSetting


def create_app() -> FastAPI:
    config = ProjectSetting.from_dotenv(env_file=getenv("ENV_FILE", ".env"))

    @asynccontextmanager
    async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        app.state.config = config
        yield
        await config.sqlalchemy.async_cleanup()

    app = FastAPI(
        **config.to_fastapi_config(),
        exception_handlers=get_error_handlers(),
        lifespan=app_lifespan,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
    )
    app.include_router(router)

    return app
