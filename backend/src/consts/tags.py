import enum


class OpenAPITag(enum.StrEnum):
    def _generate_next_value_(name: str, start: int, count: int, last_values: list[str]) -> str:  # type: ignore[override]
        return " ".join(map(str.capitalize, name.split("_")))

    HEALTH_CHECK = enum.auto()

    JSON_SCHEMA = enum.auto()

    CONFIG_NODE = enum.auto()
    DEVICE = enum.auto()
