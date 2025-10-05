from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel


class EnumValue(BaseModel):
    const: UUID
    title: str

    @classmethod
    def from_tuple(cls, tpl: tuple[UUID, str]) -> EnumValue:
        return cls(const=tpl[0], title=tpl[1])
