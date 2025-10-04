from __future__ import annotations

from typing import Literal, NotRequired, TypeAlias, TypedDict

JSONScalar = str | int | float | bool | None
JSONValue = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

JSONSchemaType = Literal["string", "number", "integer", "object", "array", "boolean", "null"]
JSONSchemaFormat = Literal[
    "date-time",
    "time",
    "date",
    "duration",
    "email",
    "idn-email",
    "hostname",
    "idn-hostname",
    "ipv4",
    "ipv6",
    "uuid",
    "uri",
    "uri-reference",
    "iri",
    "iri-reference",
    "uri-template",
    "json-pointer",
    "relative-json-pointer",
    "regex",
]


class CommonKeywords(TypedDict):
    title: NotRequired[str]
    description: NotRequired[str]

    default: NotRequired[JSONValue]
    examples: NotRequired[list[JSONValue]]
    enum: NotRequired[list[JSONValue]]
    const: NotRequired[JSONValue]

    type: NotRequired[JSONSchemaType | list[JSONSchemaType]]

    allOf: NotRequired[list[Schema]]
    anyOf: NotRequired[list[Schema]]
    oneOf: NotRequired[list[Schema]]

    # Custom keywords for UI rendering
    readOnly: NotRequired[bool]
    writeOnly: NotRequired[bool]
    deprecated: NotRequired[bool]


class StringKeywords(CommonKeywords):
    type: Literal["string"]  # type: ignore[misc]
    minLength: NotRequired[int]
    maxLength: NotRequired[int]
    pattern: NotRequired[str]
    format: NotRequired[JSONSchemaFormat]


class NumberKeywords(CommonKeywords):
    type: Literal["number"]  # type: ignore[misc]
    minimum: NotRequired[int | float]
    maximum: NotRequired[int | float]
    exclusiveMinimum: NotRequired[int | float]
    exclusiveMaximum: NotRequired[int | float]
    multipleOf: NotRequired[int | float]


class IntegerKeywords(NumberKeywords):
    type: Literal["integer"]  # type: ignore[misc]


class NullKeywords(CommonKeywords):
    type: Literal["null"]  # type: ignore[misc]


class BooleanKeywords(CommonKeywords):
    type: Literal["boolean"]  # type: ignore[misc]


class ArrayKeyworkds(CommonKeywords):
    type: Literal["array"]  # type: ignore[misc]
    prefixItems: NotRequired[list[Schema]]
    items: NotRequired[Schema]
    contains: NotRequired[Schema]
    minContains: NotRequired[int]
    maxContains: NotRequired[int]
    minItems: NotRequired[int]
    maxItems: NotRequired[int]
    uniqueItems: NotRequired[bool]
    unevaluatedItems: NotRequired[Schema]


class ObjectKeywords(CommonKeywords):
    type: Literal["object"]  # type: ignore[misc]
    properties: NotRequired[dict[str, Schema]]
    patternProperties: NotRequired[dict[str, Schema]]
    additionalProperties: NotRequired[bool | Schema]
    required: NotRequired[list[str]]
    minProperties: NotRequired[int]
    maxProperties: NotRequired[int]
    dependentRequired: NotRequired[dict[str, list[str]]]
    dependentSchemas: NotRequired[dict[str, Schema]]
    unevaluatedProperties: NotRequired[Schema]
    propertyNames: NotRequired[Schema]


Schema: TypeAlias = StringKeywords | NumberKeywords | IntegerKeywords | NullKeywords | BooleanKeywords | ArrayKeyworkds | ObjectKeywords | bool
