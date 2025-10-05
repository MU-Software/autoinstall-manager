from collections.abc import AsyncGenerator, Generator
from typing import Annotated, cast

from fastapi import Depends, FastAPI, Request
from sqlmodel.ext.asyncio.session import AsyncSession as SQLModelAsyncSession
from src.settings import ProjectSetting


def config_di(request: Request) -> Generator[ProjectSetting, None, None]:
    yield cast(ProjectSetting, cast(FastAPI, request.app).state.config)


configDI = Annotated[ProjectSetting, Depends(config_di)]


async def db_session_di(config: configDI) -> AsyncGenerator[SQLModelAsyncSession, None]:
    async with config.sqlalchemy.async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as se:
            await session.rollback()
            raise se
        finally:
            await session.aclose()


dbDI = Annotated[SQLModelAsyncSession, Depends(db_session_di)]
