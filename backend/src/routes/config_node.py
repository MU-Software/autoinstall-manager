from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import ConfigNode
from src.schemas.enum_value import EnumValue
from src.services.config_node import configNodeServiceDI

config_node_router = APIRouter(prefix="/confignode", tags=[OpenAPITag.CONFIG_NODE])


@config_node_router.get("/", response_model=Sequence[ConfigNode])
async def list_config_nodes(config_node_svc: configNodeServiceDI) -> Sequence[ConfigNode]:
    return await config_node_svc.list()


@config_node_router.get("/enum-values", response_model=Sequence[EnumValue])
async def list_config_node_enum_values(config_node_svc: configNodeServiceDI) -> Sequence[EnumValue]:
    return await config_node_svc.list_enum_values()


@config_node_router.get("/{config_node_id}", response_model=ConfigNode)
async def retrieve_config_node(config_node_id: UUID, config_node_svc: configNodeServiceDI) -> ConfigNode:
    return await config_node_svc.retrieve_by_id(id=config_node_id)


@config_node_router.post("/", response_model=ConfigNode)
async def create_config_node(config_node: ConfigNode, config_node_svc: configNodeServiceDI) -> ConfigNode:
    return await config_node_svc.create(obj=config_node)


@config_node_router.put("/", response_model=ConfigNode)
async def update_config_node(config_node: ConfigNode, config_node_svc: configNodeServiceDI) -> ConfigNode:
    return await config_node_svc.update(obj=config_node)


@config_node_router.delete("/{config_node_id}", response_model=None)
async def delete_config_node(config_node_id: UUID, config_node_svc: configNodeServiceDI) -> None:
    await config_node_svc.delete_by_id(id=config_node_id)
