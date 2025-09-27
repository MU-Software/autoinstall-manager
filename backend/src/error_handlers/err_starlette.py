from __future__ import annotations

from fastapi import Response
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from src.errors import ErrorStruct
from src.utils.strlib import camel_to_snake_case
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request


async def fastapi_http_exception_handler(req: Request, err: FastAPIHTTPException) -> Response:
    return await http_exception_handler(req, err)


async def starlette_http_exception_handler(req: Request, err: StarletteHTTPException) -> Response:
    response = ErrorStruct(
        status_code=err.status_code,
        type=camel_to_snake_case(err.__class__.__name__),
        msg=err.detail,
    ).response()
    response.headers.update(err.headers or {})
    return response


error_handler_patterns = {
    FastAPIHTTPException: fastapi_http_exception_handler,
    StarletteHTTPException: starlette_http_exception_handler,
}
