from collections.abc import Iterable
from contextlib import suppress
from typing import Any, TypeGuard


def isiterable(obj: Any) -> TypeGuard[Iterable]:
    with suppress(TypeError):
        return iter(obj) is not None
    return False


def safe_attrgetter(obj: Any, attr: str) -> Any | None:
    """Object에서 AttributeError를 발생시키지 않고 안전하게 attribute를 가져옵니다."""
    value, attr_fields = obj, attr.split(".")
    while attr_fields and (value := getattr(value, attr_fields.pop(0), None)) is not None:
        continue
    return value
