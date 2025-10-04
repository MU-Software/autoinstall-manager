from typing import TypedDict, cast

from pydantic_core import PydanticUndefinedType
from sqlmodel.main import SQLModel

from .jsonschemalib import Schema, StringKeywords


def get_foreign_key_constraints(model: type[SQLModel]) -> dict[str, str]:
    result: dict[str, str] = {}

    for field_name, field_info in model.model_fields.items():
        foreign_key: str | PydanticUndefinedType = field_info.foreign_key  # type: ignore[attr-defined]
        if isinstance(foreign_key, str):
            result[field_name] = foreign_key

    return result


class SchemaInfo(TypedDict):
    schema: Schema
    ui_schema: dict[str, dict[str, str | dict[str, str]]]


def get_json_schema(model: type[SQLModel]) -> SchemaInfo:
    foreign_keys = get_foreign_key_constraints(model)
    schema = cast(Schema, model.model_json_schema())
    ui_schema: dict[str, dict[str, str | dict[str, str]]] = {}

    # for type checking
    assert isinstance(schema, dict)  # nosec B101

    def handle_foreign_key_properties(property_name: str, property_info: StringKeywords) -> None:
        if not (foreign_key := foreign_keys.get(property_name)):
            return

        property_info |= {"minLength": 36, "maxLength": 36, "format": "uuid"}
        ui_schema[property_name] = {
            "ui:widget": "ForeignKeyWidget",
            "ui:options": {"resourceName": foreign_key.split(".")[0]},
        }

    for property_name, property_info in cast(dict[str, Schema], schema.get("properties", {})).items():
        if isinstance(property_info, bool):
            continue

        if isinstance(property_info, dict) and property_info.get("type") == "string":
            handle_foreign_key_properties(property_name, cast(StringKeywords, property_info))

    return SchemaInfo(schema=schema, ui_schema=ui_schema)
