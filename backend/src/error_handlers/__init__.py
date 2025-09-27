from __future__ import annotations

from collections.abc import Callable, Coroutine
from inspect import isawaitable
from logging import getLogger
from pathlib import Path
from traceback import format_exception
from typing import Any, TypeAlias

from src.utils.importlib import auto_import_patterns
from starlette.requests import Request
from starlette.responses import Response

logger = getLogger(__name__)
ErrHandlerType: TypeAlias = Callable[[Request, Any], Coroutine[Any, Any, Response]]


def get_error_handlers() -> dict[int | type[Exception], ErrHandlerType]:
    error_handler_collection: list[dict[int | type[Exception], ErrHandlerType]] = auto_import_patterns(
        "error_handler_patterns",
        "err_",
        Path(__file__).parent,
    )

    def error_logger_decorator(err_handler: ErrHandlerType) -> ErrHandlerType:
        async def wrapper(req: Request, err: Exception) -> Response:
            logger.warning("".join(format_exception(err)))
            return (await response) if isawaitable(response := err_handler(req, err)) else response

        return wrapper

    return {k: error_logger_decorator(v) for d in error_handler_collection for k, v in d.items()}
