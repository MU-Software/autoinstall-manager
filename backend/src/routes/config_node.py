from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import ConfigNode
from src.repositories import EnumValue
from src.repositories.config_node import configNodeRepoDI

config_node_router = APIRouter(prefix="/confignode", tags=[OpenAPITag.CONFIG_NODE])


@config_node_router.get("/", response_model=Sequence[ConfigNode])
async def list_config_nodes(config_node_repo: configNodeRepoDI) -> Sequence[ConfigNode]:
    return await config_node_repo.list()


@config_node_router.get("/enum-values", response_model=Sequence[EnumValue])
async def list_config_node_enum_values(config_node_repo: configNodeRepoDI) -> Sequence[EnumValue]:
    return await config_node_repo.list_enum_values()


@config_node_router.get("/{config_node_id}", response_model=ConfigNode)
async def retrieve_config_node(config_node_id: UUID, config_node_repo: configNodeRepoDI) -> ConfigNode:
    return await config_node_repo.retrieve_by_id(id=config_node_id)
