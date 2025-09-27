from __future__ import annotations

from json import JSONDecodeError

from src.errors import ClientError, ErrorStruct, ServerError
from starlette.requests import Request
from starlette.responses import JSONResponse


async def valueerror_handler(req: Request, err: ValueError) -> JSONResponse:
    return ErrorStruct.from_exception(err).response()


async def jsondecodeerror_handler(req: Request, err: JSONDecodeError) -> JSONResponse:
    context = {"pos": err.pos, "lineno": err.lineno, "colno": err.colno, "msg": err.msg}
    return ClientError.JSON_DECODE_ERROR.response(input=err.doc, ctx=context)


async def exception_handler(req: Request, err: Exception) -> JSONResponse:
    return ServerError.UNKNOWN_SERVER_ERROR.response()


error_handler_patterns = {
    JSONDecodeError: jsondecodeerror_handler,
    ValueError: valueerror_handler,
    Exception: exception_handler,
}
