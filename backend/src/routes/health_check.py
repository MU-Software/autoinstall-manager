from logging import getLogger
from typing import Literal

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.sql import text
from src.consts.tags import OpenAPITag
from src.dependencies import configDI, dbDI

logger = getLogger(__name__)

health_check_router = APIRouter(prefix="/health", tags=[OpenAPITag.HEALTH_CHECK])


class EmptyResponseSchema(BaseModel):
    message: Literal["ok"] = "ok"


class ReadyzResponse(EmptyResponseSchema):
    debug: bool
    version: str
    database: bool = True

    @property
    def status_code(self) -> int:
        return status.HTTP_200_OK if self.database else status.HTTP_500_INTERNAL_SERVER_ERROR


@health_check_router.get("/livez", response_model=EmptyResponseSchema)
async def livez() -> dict[str, str]:
    return {"message": "ok"}


@health_check_router.get(
    "/readyz",
    response_model=ReadyzResponse,
    responses={
        status.HTTP_200_OK: {"model": ReadyzResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ReadyzResponse},
    },
)
async def readyz(config: configDI, db: dbDI) -> JSONResponse:
    content = ReadyzResponse(debug=config.server.debug, version=config.project_info.version)

    try:
        await db.scalar(text("SELECT 1"))
    except Exception as err:
        logger.error("DB connection failed", exc_info=err)
        content.database = False

    return JSONResponse(status_code=content.status_code, content=content.model_dump())
