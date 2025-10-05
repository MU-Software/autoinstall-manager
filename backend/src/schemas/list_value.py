from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ListValue(BaseModel):
    id: UUID
    title: str
    created_at: datetime | None
    updated_at: datetime | None

    @classmethod
    def from_tuple(cls, tpl: tuple[UUID, str, datetime | None, datetime | None]) -> ListValue:
        return cls(id=tpl[0], title=tpl[1], created_at=tpl[2], updated_at=tpl[3])
