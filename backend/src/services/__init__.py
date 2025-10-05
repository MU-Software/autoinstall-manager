from collections.abc import Sequence
from typing import Generic, TypeVar, Unpack
from uuid import UUID

from pydantic import BaseModel
from src.models import DefaultModelMixin
from src.repositories import ListKwargsType, QueryType, RepositoryImpl
from src.schemas.enum_value import EnumValue
from src.schemas.list_value import ListValue

M = TypeVar("M", bound=DefaultModelMixin)


class ServiceImpl(BaseModel, Generic[M]):
    repository: RepositoryImpl[M]

    async def count(self, filter: QueryType | None = None) -> int:
        return await self.repository.count(filter=filter)

    async def retrieve_by_query(self, filter: QueryType) -> M:
        return await self.repository.retrieve_by_query(filter=filter)

    async def retrieve_by_id(self, id: UUID) -> M:
        return await self.repository.retrieve_by_id(id=id)

    async def list(self, **kwargs: Unpack[ListKwargsType]) -> Sequence[M]:
        return await self.repository.list(**kwargs)

    async def create(self, obj: M) -> M:
        return await self.repository.create(obj=obj)

    async def update(self, obj: M) -> M:
        return await self.repository.update(obj=obj)

    async def delete(self, obj: M) -> None:
        await self.repository.delete(obj=obj)

    async def delete_by_id(self, id: UUID) -> None:
        await self.repository.delete_by_id(id=id)

    async def list_values(self) -> Sequence[ListValue]:
        return await self.repository.list_values()

    async def list_enum_values(self) -> Sequence[EnumValue]:
        return await self.repository.list_enum_values()
