from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import func
from sqlmodel.sql.expression import any_, col, not_, select
from src.models import ConfigNode, Device
from src.repositories import EnumValue, RepositoryImpl


class DeviceRepository(RepositoryImpl[Device]):
    model = Device

    async def list_enum_values(self) -> Sequence[EnumValue]:
        # ConfigNodeRepository.list_enum_values()의 CTE 로직과 유사
        confignode_children = aliased(ConfigNode, name="confignode_children")

        config_node_seed = (
            select(
                ConfigNode.id,
                ConfigNode.parent_id,
                col(ConfigNode.name).label("path"),
                array([ConfigNode.id]).label("visited"),
            )
            .where(col(ConfigNode.parent_id).is_(None))
            .cte("tree", recursive=True)
        )
        config_node_tree = config_node_seed.union_all(
            select(
                confignode_children.id,
                confignode_children.parent_id,
                func.concat(config_node_seed.c.path, " > ", confignode_children.name).label("path"),
                func.array_cat(config_node_seed.c.visited, array([confignode_children.id])).label("visited"),
            )
            .join(config_node_seed, col(confignode_children.parent_id) == col(config_node_seed.c.id))
            .where(not_(confignode_children.id == any_(config_node_seed.c.visited)))
        )
        query = (
            select(self.model.id, func.concat("Device: ", self.model.name, "(", self.model.id, ")", "[", config_node_tree.c.path, "]"))
            .select_from(self.model)
            .join(config_node_tree, col(self.model.config_node_id) == col(config_node_tree.c.id))
        )
        return [EnumValue.from_tuple(row) for row in await self.session.exec(query)]


deviceRepoDI = Annotated[DeviceRepository, Depends(DeviceRepository)]
