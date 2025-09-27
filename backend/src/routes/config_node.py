from collections.abc import Sequence

from fastapi import APIRouter
from src.models import ConfigNode
from src.repositories.config_node import configNodeRepoDI

config_node_router = APIRouter(prefix="/config-nodes")

"""
endpoint 목록
- config node list / retrieve / create / update / delete
"""


@config_node_router.get("/", response_model=Sequence[ConfigNode])
async def list_config_nodes(config_node_repo: configNodeRepoDI) -> Sequence[ConfigNode]:
    return await config_node_repo.list()
