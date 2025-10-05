from typing import TypedDict, cast

from pydantic_core import PydanticUndefinedType
from sqlmodel.main import SQLModel

from .jsonschemalib import Schema

READ_ONLY_COLUMNS = ("id", "created_at", "updated_at")


def get_foreign_key_constraints(model: type[SQLModel]) -> dict[str, str]:
    result: dict[str, str] = {}

    for field_name, field_info in model.model_fields.items():
        foreign_key: str | PydanticUndefinedType = field_info.foreign_key  # type: ignore[attr-defined]
        if isinstance(foreign_key, str):
            result[field_name] = foreign_key

    return result


class SchemaInfo(TypedDict):
    schema: Schema
    ui_schema: dict[str, dict[str, str | bool | dict[str, str]]]


def get_json_schema(model: type[SQLModel]) -> SchemaInfo:
    foreign_keys = get_foreign_key_constraints(model)
    schema = cast(Schema, model.model_json_schema())
    ui_schema: dict[str, dict[str, str | bool | dict[str, str]]] = {}

    # for type checking
    assert isinstance(schema, dict)  # nosec B101

    def is_read_only_property(property_name: str, property_info: Schema) -> bool:
        if not isinstance(property_info, dict):
            return False

        return property_info.get("readOnly") or property_name in READ_ONLY_COLUMNS

    def is_foreign_key_property(property_name: str, property_info: Schema, allow_recursive: bool = True) -> bool:
        if not isinstance(property_info, dict):
            return False

        if "type" not in property_info:
            if not allow_recursive:  # type: ignore[unreachable]
                return False

            # This might be a anyOf, oneOf, etc.
            # If anyOf or oneOf field contains only two schemas and one of them is null, it is considered as nullable field.
            # Check the other schema's type.
            for keyword in ("anyOf", "oneOf"):
                if keyword not in property_info:
                    continue

                for sub_property_info in property_info[keyword]:
                    if is_foreign_key_property(property_name, sub_property_info, False):
                        return True

            return False

        return property_info.get("type") == "string" and property_info.get("format") == "uuid" and property_name in foreign_keys

    def handle_foreign_key_property(property_name: str, _: Schema) -> None:
        ui_schema[property_name] = {
            "ui:field": "ForeignKeyField",
            "ui:fieldReplacesAnyOrOneOf": True,
            "ui:options": {"resourceName": foreign_keys[property_name].split(".")[0]},
        }

    for property_name, property_info in cast(dict[str, Schema], schema.get("properties", {})).items():
        if isinstance(property_info, bool):
            continue

        if is_read_only_property(property_name, property_info):
            continue

        if is_foreign_key_property(property_name, property_info):
            handle_foreign_key_property(property_name, property_info)

    return SchemaInfo(schema=schema, ui_schema=ui_schema)
