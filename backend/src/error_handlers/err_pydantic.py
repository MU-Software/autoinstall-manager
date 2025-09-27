from __future__ import annotations

from fastapi import status
from pydantic_core import ValidationError
from starlette.requests import Request
from starlette.responses import JSONResponse


async def pydantic_validationerror_handler(req: Request, err: ValidationError) -> JSONResponse:
    try:
        print(err.errors(include_context=False))
        print(err.args)
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=err.errors(include_context=False),
        )
    except TypeError:
        # Maybe this might be caused by invalid input data. Let's exclude it and retry.
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=err.errors(include_context=False, include_input=False),
        )


error_handler_patterns = {ValidationError: pydantic_validationerror_handler}
