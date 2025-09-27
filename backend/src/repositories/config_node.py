from typing import Annotated

from fastapi import Depends
from src.models import ConfigNode
from src.repositories import RepositoryImpl


class ConfigNodeRepository(RepositoryImpl[ConfigNode]):
    model = ConfigNode


configNodeRepoDI = Annotated[ConfigNodeRepository, Depends(ConfigNodeRepository)]
