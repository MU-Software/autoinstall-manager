from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import ConfigNode
from src.repositories.config_node import configNodeRepoDI

config_node_router = APIRouter(prefix="/config-nodes", tags=[OpenAPITag.CONFIG_NODE])

"""
endpoint 목록
- config node list / retrieve / create / update / delete
"""


@config_node_router.get("/", response_model=Sequence[ConfigNode])
async def list_config_nodes(config_node_repo: configNodeRepoDI) -> Sequence[ConfigNode]:
    return await config_node_repo.list()


@config_node_router.get("/{config_node_id}", response_model=ConfigNode)
async def retrieve_config_nodes(config_node_id: UUID, config_node_repo: configNodeRepoDI) -> ConfigNode:
    return await config_node_repo.retrieve_by_id(id=config_node_id)
