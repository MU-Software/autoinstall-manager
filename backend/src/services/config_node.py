from typing import Annotated

from fastapi import Depends
from src.models import ConfigNode
from src.repositories.config_node import configNodeRepoDI
from src.services import ServiceImpl


class ConfigNodeService(ServiceImpl[ConfigNode]):
    repository: configNodeRepoDI


configNodeServiceDI = Annotated[ConfigNodeService, Depends(ConfigNodeService)]
