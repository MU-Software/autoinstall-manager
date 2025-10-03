from collections.abc import Sequence
from typing import ClassVar, Generic, NotRequired, TypeAlias, TypedDict, TypeVar, Unpack
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.expression import ColumnElement, desc, func, select, true
from src.consts.errors import ClientError, ServerError
from src.dependencies import dbDI
from src.models import DefaultModelMixin

M = TypeVar("M", bound=DefaultModelMixin)

QueryType: TypeAlias = ColumnElement[bool]
OrderByType: TypeAlias = list[ColumnElement | UnaryExpression | str]


class ListKwargsType(TypedDict, total=False):
    filter: NotRequired[QueryType]
    order_by: NotRequired[OrderByType]
    offset: NotRequired[int]
    limit: NotRequired[int]


class RepositoryImpl(BaseModel, Generic[M]):
    session: dbDI

    model: ClassVar[type[M]]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def order_by(self) -> OrderByType:
        return [desc(self.model.updated_at)]  # type: ignore[arg-type]

    async def count(self, filter: QueryType | None = None) -> int:
        query = select(func.count()).select_from(self.model).where(filter or true())
        return (await self.session.scalar(query)) or 0

    async def retrieve_by_query(self, filter: QueryType) -> M:
        try:
            query = select(self.model).where(filter)
            return (await self.session.scalars(query)).one()
        except NoResultFound:
            ClientError.RESOURCE_NOT_FOUND.raise_()
        except MultipleResultsFound:
            ServerError.MULTIPLE_RESOURCES_FOUND.raise_()

    async def retrieve_by_id(self, id: UUID | str) -> M:
        return await self.retrieve_by_query(self.model.id == id)  # type: ignore[arg-type]

    async def list(self, **kwargs: Unpack[ListKwargsType]) -> Sequence[M]:
        filter: QueryType = kwargs.get("filter", true())
        order_by: OrderByType = kwargs.get("order_by", self.order_by)
        offset: int | None = kwargs.get("offset", None)
        limit: int | None = kwargs.get("limit", None)

        query = select(self.model).where(filter).order_by(*order_by).offset(offset).limit(limit)
        return (await self.session.scalars(query)).all()

    async def create(self, obj: M) -> M:
        self.session.add(obj)
        await self.session.commit()
        return obj

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)
        await self.session.commit()
        return None
