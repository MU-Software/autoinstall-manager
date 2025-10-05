from sqlalchemy.dialects.postgresql import array
from sqlalchemy.orm import aliased
from sqlalchemy.sql.elements import literal
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.selectable import CTE
from sqlmodel.sql.expression import any_, col, not_, or_, select
from src.models import ConfigNode


class ConfigNodeQuery:
    @staticmethod
    def get_nested_title_cte() -> CTE:
        parent = aliased(ConfigNode, name="parent")
        children = aliased(ConfigNode, name="children")

        seed = (
            select(
                ConfigNode.id,
                ConfigNode.parent_id,
                col(ConfigNode.name).label("path"),
                array([ConfigNode.id]).label("visited"),
            )
            .select_from(ConfigNode)
            .outerjoin(parent, col(ConfigNode.parent_id) == col(parent.id))
            .where(or_(col(ConfigNode.parent_id).is_(None), col(parent.id).is_(None)))
            .cte("tree", recursive=True)
        )
        return seed.union_all(
            select(
                children.id,
                children.parent_id,
                func.concat_ws(literal(" > "), col(seed.c.path), col(children.name)).label("path"),
                func.array_cat(seed.c.visited, array([children.id])).label("visited"),
            )
            .join(seed, col(children.parent_id) == col(seed.c.id))
            .where(not_(children.id == any_(seed.c.visited)))
        )
