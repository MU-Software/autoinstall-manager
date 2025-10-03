from typing import Any

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import ConfigNode, Device
from src.schemas.autoinstall import Autoinstall

json_schema_router = APIRouter(prefix="/json-schemas", tags=[OpenAPITag.JSON_SCHEMA])


@json_schema_router.get("/autoinstall", response_model=dict[str, Any])
async def get_autoinstall_json_schema() -> dict[str, Any]:  # type: ignore[misc]
    return Autoinstall.model_json_schema()


@json_schema_router.get("/config-nodes", response_model=dict[str, Any])
async def get_config_node_json_schema() -> dict[str, Any]:  # type: ignore[misc]
    return ConfigNode.model_json_schema()


@json_schema_router.get("/devices", response_model=dict[str, Any])
async def get_device_json_schema() -> dict[str, Any]:  # type: ignore[misc]
    return Device.model_json_schema()
