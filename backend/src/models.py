from datetime import datetime
from re import Pattern, compile
from secrets import token_hex
from typing import Annotated, Literal, NamedTuple, Unpack
from uuid import UUID, uuid4

from pydantic import ConfigDict, PlainSerializer, computed_field
from sqlalchemy.orm import declared_attr
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import MetaData
from sqlmodel import Field, SQLModel


class NCType(NamedTuple):
    name: str
    regex: Pattern


NCKeyType = Literal["ix", "uq", "ck", "fk", "pk"]
NAMING_CONVENTION_DICT: dict[NCKeyType, NCType] = {
    "ix": NCType(
        "ix_%(column_0_label)s",
        compile(r"^ix_(?P<table_name>.+)_(?P<column_0_name>.+)$"),
    ),
    "uq": NCType(
        "uq_%(table_name)s_%(column_0_name)s",
        compile(r"^uq_(?P<table_name>.+)_(?P<column_0_name>.+)$"),
    ),
    "ck": NCType(
        "ck_%(table_name)s_%(constraint_name)s",
        compile(r"^ck_(?P<table_name>.+)_(?P<constraint_name>.+)$"),
    ),
    "pk": NCType("pk_%(table_name)s", compile(r"^pk_(?P<table_name>.+)$")),
    "fk": NCType(
        "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        compile(r"^fk_(?P<table_name>.+)_(?P<column_0_name>.+)_(?P<referred_table_name>.+)$"),
    ),
}
MODELS: dict[str, type[SQLModel]] = {}
default_model_mixin_metadata = MetaData(naming_convention={k: v.name for k, v in NAMING_CONVENTION_DICT.items()})


UUIDSerializer = PlainSerializer(func=str, return_type=str, when_used="json-unless-none")
UUIDField = Annotated[UUID, UUIDSerializer]
NullableUUIDField = Annotated[UUID | None, UUIDSerializer]


class DefaultModelMixin(SQLModel, table=False):
    id: Annotated[
        UUIDField,
        Field(
            primary_key=True,
            index=True,
            nullable=False,
            default_factory=uuid4,
            schema_extra={"json_schema_extra": {"readOnly": True}},
        ),
    ]

    created_at: Annotated[
        datetime | None,
        Field(
            nullable=False,
            sa_column_kwargs={"server_default": func.now()},
            schema_extra={"json_schema_extra": {"readOnly": True}},
        ),
    ] = None
    updated_at: Annotated[
        datetime | None,
        Field(
            nullable=False,
            sa_column_kwargs={"server_default": func.now(), "server_onupdate": func.now()},
            schema_extra={"json_schema_extra": {"readOnly": True}},
        ),
    ] = None

    metadata = default_model_mixin_metadata

    @declared_attr  # type: ignore[arg-type]
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    @computed_field  # type: ignore[prop-decorator]  # See https://github.com/python/mypy/issues/1362
    @property
    def representation(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    @classmethod
    def __init_subclass__(cls, *args: tuple, **kwargs: Unpack[ConfigDict]) -> None:
        super().__init_subclass__(*args, **kwargs)
        MODELS[cls.__name__] = cls


class ConfigNode(DefaultModelMixin, table=True):
    name: Annotated[str, Field(nullable=False, index=True, unique=True)]
    parent_id: Annotated[
        UUIDField | None,
        Field(foreign_key="confignode.id", nullable=True, default=None),
    ]

    autoinstall_config: Annotated[str, Field(nullable=False)]  # JSON serialized value

    @computed_field  # type: ignore[prop-decorator]  # See DefaultModelMixin.representation
    @property
    def representation(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"


class Device(DefaultModelMixin, table=True):
    name: Annotated[str, Field(nullable=False, index=True, unique=True)]
    identifier: Annotated[
        str,
        Field(
            nullable=False,
            index=True,
            unique=True,
            default_factory=lambda: token_hex(16),
        ),
    ]

    config_node_id: Annotated[UUID, Field(foreign_key="confignode.id", nullable=False)]

    @computed_field  # type: ignore[prop-decorator]  # See DefaultModelMixin.representation
    @property
    def representation(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"
