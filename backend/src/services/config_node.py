from typing import Annotated, NoReturn
from uuid import UUID

from fastapi import Depends
from src.consts.errors import ClientError
from src.models import ConfigNode
from src.repositories.config_node import configNodeRepoDI
from src.services import ServiceImpl


class ConfigNodeService(ServiceImpl[ConfigNode]):
    repository: configNodeRepoDI

    async def _check_cycle(self, node: ConfigNode) -> None:
        def _raise_validation_error(msg: str) -> NoReturn:
            ClientError.REQUEST_BODY_INVALID(type="value_error", msg=msg, loc=["parent_id"], input=node.parent_id).raise_()

        if not node.parent_id:
            return

        nodes: dict[UUID, ConfigNode] = {n.id: n for n in await self.repository.list()}
        parent = nodes.get(node.parent_id)
        while parent:
            if parent.id == node.id:
                _raise_validation_error("부모 설정이 순환 참조를 발생시킵니다.")

            if not parent.parent_id:
                break

            parent = nodes.get(parent.parent_id)

    async def create(self, obj: ConfigNode) -> ConfigNode:
        await self._check_cycle(obj)
        return await super().create(obj)

    async def update(self, obj: ConfigNode) -> ConfigNode:
        await self._check_cycle(obj)
        return await super().update(obj)


configNodeServiceDI = Annotated[ConfigNodeService, Depends(ConfigNodeService)]
