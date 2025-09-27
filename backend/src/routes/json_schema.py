from typing import Any

from fastapi import APIRouter
from src.schemas.autoinstall import Autoinstall

json_schema_router = APIRouter(prefix="/jsonschemas")


@json_schema_router.get("/autoinstall", response_model=dict[str, Any])
async def get_autoinstall_json_schema() -> dict[str, Any]:  # type: ignore[misc]
    return Autoinstall.model_json_schema()
