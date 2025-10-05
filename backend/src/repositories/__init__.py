from __future__ import annotations

from collections.abc import Sequence
from typing import ClassVar, Generic, TypeAlias, TypedDict, TypeVar, Unpack
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.sql.elements import UnaryExpression
from sqlalchemy.sql.expression import ColumnElement, func, select, true
from sqlmodel.sql.expression import col, desc
from src.consts.errors import ClientError, ServerError
from src.dependencies import dbDI
from src.models import DefaultModelMixin
from src.schemas.enum_value import EnumValue

M = TypeVar("M", bound=DefaultModelMixin)

QueryType: TypeAlias = ColumnElement[bool]
OrderExpr: TypeAlias = ColumnElement | UnaryExpression
OrderByType: TypeAlias = list[OrderExpr]

DEFAULT_NOT_MODIFIABLE_FIELDS = {"id", "created_at", "updated_at"}


class ListKwargsType(TypedDict, total=False):
    filter: QueryType
    order_by: OrderByType
    offset: int
    limit: int


class RepositoryImpl(BaseModel, Generic[M]):
    session: dbDI

    model: ClassVar[type[M]]
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def order_by(self) -> OrderByType:
        return [desc(self.model.updated_at)]

    async def count(self, filter: QueryType | None = None) -> int:
        query = select(func.count()).select_from(self.model).where(filter or true())
        return (await self.session.scalar(query)) or 0

    async def retrieve_by_query(self, filter: QueryType, with_for_update: bool = False) -> M:
        try:
            query = select(self.model).where(filter)
            if with_for_update:
                query = query.with_for_update()

            return (await self.session.scalars(query)).one()
        except NoResultFound:
            ClientError.RESOURCE_NOT_FOUND.raise_()
        except MultipleResultsFound:
            ServerError.MULTIPLE_RESOURCES_FOUND.raise_()

    async def retrieve_by_id(self, id: UUID, with_for_update: bool = False) -> M:
        return await self.retrieve_by_query(col(self.model.id) == id, with_for_update=with_for_update)

    async def list(self, **kwargs: Unpack[ListKwargsType]) -> Sequence[M]:
        filter: QueryType = kwargs.get("filter", true())
        order_by: OrderByType = kwargs.get("order_by", self.order_by)
        offset: int | None = kwargs.get("offset", None)
        limit: int | None = kwargs.get("limit", None)

        query = select(self.model).where(filter).order_by(*order_by).offset(offset).limit(limit)
        return (await self.session.scalars(query)).all()

    async def create(self, obj: M) -> M:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: M) -> M:
        if not obj.id:
            ClientError.REQUEST_BODY_LACK.raise_()

        db_obj = await self.retrieve_by_id(id=obj.id, with_for_update=True)
        for key, value in obj.model_dump(exclude_unset=True, exclude=DEFAULT_NOT_MODIFIABLE_FIELDS).items():
            setattr(db_obj, key, value)

        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)

    async def delete_by_id(self, id: UUID) -> None:
        await self.delete(obj=await self.retrieve_by_id(id=id, with_for_update=True))

    async def list_enum_values(self) -> Sequence[EnumValue]:
        raise NotImplementedError("subclasses must implement list_enum_values")
