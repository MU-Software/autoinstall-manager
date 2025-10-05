from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import literal
from sqlalchemy.sql.expression import func
from sqlmodel.sql.expression import any_, col, not_, or_, select
from src.models import ConfigNode
from src.repositories import RepositoryImpl
from src.schemas.enum_value import EnumValue


class ConfigNodeRepository(RepositoryImpl[ConfigNode]):
    model = ConfigNode

    async def list_enum_values(self) -> Sequence[EnumValue]:
        parent = aliased(self.model, name="parent")
        children = aliased(self.model, name="children")

        seed = (
            select(
                self.model.id,
                self.model.parent_id,
                col(self.model.name).label("path"),
                array([self.model.id]).label("visited"),
            )
            .select_from(self.model)
            .outerjoin(parent, col(self.model.parent_id) == col(parent.id))
            .where(or_(col(self.model.parent_id).is_(None), col(parent.id).is_(None)))
            .cte("tree", recursive=True)
        )
        tree = seed.union_all(
            select(
                children.id,
                children.parent_id,
                func.concat_ws(literal(" > "), col(seed.c.path), col(children.name)).label("path"),
                func.array_cat(seed.c.visited, array([children.id])).label("visited"),
            )
            .join(seed, col(children.parent_id) == col(seed.c.id))
            .where(not_(children.id == any_(seed.c.visited)))
        )

        return [EnumValue.from_tuple(row) for row in await self.session.exec(select(tree.c.id, tree.c.path))]


configNodeRepoDI = Annotated[ConfigNodeRepository, Depends(ConfigNodeRepository)]
