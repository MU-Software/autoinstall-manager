from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy.sql.expression import func
from sqlmodel.sql.expression import col, select
from src.models import Device
from src.queries.config_node import ConfigNodeQuery
from src.repositories import RepositoryImpl
from src.schemas.enum_value import EnumValue
from src.schemas.list_value import ListValue


class DeviceRepository(RepositoryImpl[Device]):
    model = Device

    async def list_values(self) -> Sequence[ListValue]:
        tree = ConfigNodeQuery.get_nested_title_cte()
        result = await self.session.exec(
            select(
                self.model.id,
                func.concat(self.model.name, " (using config-node='", tree.c.path, "')"),
                self.model.created_at,
                self.model.updated_at,
            )
            .select_from(self.model)
            .join(tree, col(self.model.config_node_id) == col(tree.c.id))
        )
        return [ListValue.from_tuple(row) for row in result]

    async def list_enum_values(self) -> Sequence[EnumValue]:
        tree = ConfigNodeQuery.get_nested_title_cte()
        result = await self.session.exec(
            select(self.model.id, func.concat(self.model.name, " (using config-node='", tree.c.path, "')"))
            .select_from(self.model)
            .join(tree, col(self.model.config_node_id) == col(tree.c.id))
        )
        return [EnumValue.from_tuple(row) for row in result]


deviceRepoDI = Annotated[DeviceRepository, Depends(DeviceRepository)]
