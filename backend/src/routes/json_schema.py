from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import ConfigNode, Device
from src.utils.third_parties.sqlmodellib import SchemaInfo, get_json_schema

json_schema_router = APIRouter(prefix="/json-schemas", tags=[OpenAPITag.JSON_SCHEMA])


@json_schema_router.get("/confignode", response_model=None)
async def get_config_node_json_schema() -> SchemaInfo:
    return get_json_schema(ConfigNode)


@json_schema_router.get("/device", response_model=None)
async def get_device_json_schema() -> SchemaInfo:
    return get_json_schema(Device)
