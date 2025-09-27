from __future__ import annotations

from enum import StrEnum
from logging import getLogger
from typing import Any, NoReturn, NotRequired, TypedDict, Unpack, cast

from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import BaseModel, Field, HttpUrl
from src.utils.strlib import camel_to_snake_case
from starlette.responses import JSONResponse

logger = getLogger(__name__)


class ErrorStructDict(TypedDict):
    type: NotRequired[str]
    msg: NotRequired[str]
    loc: NotRequired[list[str]]
    input: NotRequired[Any]
    ctx: NotRequired[dict[str, Any]]
    url: NotRequired[str]

    status_code: NotRequired[int]
    should_log: NotRequired[bool]


class ErrorStruct(BaseModel):
    type: str
    msg: str
    loc: list[str] | None = None
    input: Any | None = None
    ctx: dict[str, Any] | None = None
    url: HttpUrl | str | None = None

    status_code: int = Field(default=status.HTTP_500_INTERNAL_SERVER_ERROR, exclude=True)
    should_log: bool = Field(default=True, exclude=True)

    @classmethod
    def from_exception(cls, err: Exception) -> ErrorStruct:
        return cls(
            type=camel_to_snake_case(err.__class__.__name__),
            msg=str(err),
            loc=getattr(err, "loc", None),
            input=getattr(err, "input", None),
            ctx=getattr(err, "ctx", None),
            url=getattr(err, "url", None),
        )

    def __call__(self, **kwargs: Unpack[ErrorStructDict]) -> ErrorStruct:
        return self.model_copy(update=kwargs)

    def __repr__(self) -> str:
        result = f"{self.type}:{self.status_code}:{self.msg}"
        result += f"({self.input=})" if self.input else ""
        result += f"({self.loc=})" if self.loc else ""
        return result

    def format_msg(self, *args: object, **kwargs: object) -> ErrorStruct:
        return self(msg=self.msg.format(*args, **kwargs))

    def raise_(self) -> NoReturn:
        if self.should_log:
            logger.error(repr(self))
        if self.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
            raise RequestValidationError(errors=[self])
        raise HTTPException(
            status_code=self.status_code,
            detail=[self.model_dump(exclude_none=True, exclude_defaults=True)],
        )

    @classmethod
    def raise_multiple(cls, errors: list[ErrorStruct]) -> NoReturn:
        status_codes: set[int] = {e.status_code for e in errors}
        status_code: int = max(status_codes) if len(status_codes) > 1 else status_codes.pop()
        if status_code == status.HTTP_422_UNPROCESSABLE_CONTENT:
            raise RequestValidationError(errors=errors)
        raise HTTPException(
            status_code=status_code,
            detail=[e.model_dump(exclude_none=True, exclude_defaults=True) for e in errors],
        )

    def response(self) -> JSONResponse:
        content = {"detail": [self.model_dump(exclude_none=True, exclude_defaults=True)]}
        return JSONResponse(status_code=self.status_code, content=content)


class ErrorEnumMixin:
    __default_args__: ErrorStructDict = {}
    __additional_args__: dict[str, ErrorStructDict] = {}


class ErrorEnum(ErrorEnumMixin, StrEnum):
    _ignore_ = ["__default_args__", "__additional_args__"]

    def __call__(self, **kwargs: Unpack[ErrorStructDict]) -> ErrorStruct:
        return ErrorStruct(
            **cast(
                ErrorStructDict,
                {
                    "type": camel_to_snake_case(f"{self.__class__.__name__}.{self.name}"),
                    "msg": self.value,
                    **self.__default_args__,
                    **self.__additional_args__.get(self.name, {}),
                    **kwargs,
                },
            )
        )

    def raise_(self, **kwargs: Unpack[ErrorStructDict]) -> NoReturn:
        self(**kwargs).raise_()

    def response(self, **kwargs: Unpack[ErrorStructDict]) -> JSONResponse:
        return self(**kwargs).response()

    def format_msg(self, *args: object, **kwargs: object) -> ErrorStruct:
        err_struct = self()
        return err_struct(msg=err_struct.msg.format(*args, **kwargs))


class ServerError(ErrorEnum):
    __default_args__ = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "should_log": True,
    }

    UNKNOWN_SERVER_ERROR = "알 수 없는 문제가 발생했습니다, 5분 후에 다시 시도해주세요."
    CRITICAL_SERVER_ERROR = "서버에 치명적인 문제가 발생했습니다, 관리자에게 문의해주시면 감사하겠습니다."
    NOT_ALLOWED_LOGIC_CALLED = "예상하지 못한 문제가 발생했습니다, 관리자에게 문의해주시면 감사하겠습니다."
    MULTIPLE_RESOURCES_FOUND = "내부적으로 하나의 데이터를 예상한 곳에서 여러 개의 데이터가 조회되어 문제가 생겼어요, 관리자에게 문의해주세요."


class DBServerError(ErrorEnum):
    __default_args__ = {
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "should_log": True,
    }

    DB_CONNECTION_ERROR = "알 수 없는 문제가 발생했습니다, 5분 후에 다시 시도해주세요."
    DB_INTERFACE_ERROR = "알 수 없는 문제가 발생했습니다, 5분 후에 다시 시도해주세요."
    DB_UNKNOWN_ERROR = "알 수 없는 문제가 발생했습니다, 5분 후에 다시 시도해주세요."
    DB_CRITICAL_ERROR = "서버에 치명적인 문제가 발생했습니다, 관리자에게 문의해주시면 감사하겠습니다."
    DB_INTEGRITY_CONSTRAINT_ERROR = "기존에 저장된 데이터가 완전하거나 정확하지 않아요, 관리자에게 문의해주세요."


class DBValueError(ErrorEnum):
    __default_args__ = {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "should_log": True,
    }

    DB_DATA_ERROR = "올바르지 않은 값이에요, 다른 값을 입력해주세요."
    DB_UNIQUE_CONSTRAINT_ERROR = "이미 등록되어 있어서 사용할 수 없어요, 다른 값을 입력해주세요."
    DB_FOREIGN_KEY_CONSTRAINT_ERROR = "{referred_table_name}에 해당 값이 존재하지 않아요, 다른 값을 입력해주세요."
    DB_NOT_NULL_CONSTRAINT_ERROR = "이 값은 필수 값이에요, 값을 입력해주세요."
    DB_RESTRICT_CONSTRAINT_ERROR = "다른 곳에서 사용하고 있어서 수정하거나 삭제할 수 없어요."
    DB_CHECK_CONSTRAINT_ERROR = "조건에 맞지 않아 등록할 수 없어요, 다른 값을 입력해주세요."
    DB_EXCLUSION_CONSTRAINT_ERROR = "다른 곳에 이미 등록되어 있어서 사용할 수 없어요, 다른 값을 입력해주세요."


class ClientError(ErrorEnum):
    __default_args__ = {
        "status_code": status.HTTP_422_UNPROCESSABLE_CONTENT,
        "should_log": False,
    }
    __additional_args__ = {
        "API_NOT_FOUND": ErrorStructDict(status_code=status.HTTP_404_NOT_FOUND),
        "RESOURCE_NOT_FOUND": ErrorStructDict(status_code=status.HTTP_404_NOT_FOUND),
        "JSON_DECODE_ERROR": ErrorStructDict(status_code=status.HTTP_400_BAD_REQUEST),
        "REQUEST_TOO_FREQUENT": ErrorStructDict(status_code=status.HTTP_429_TOO_MANY_REQUESTS),
        "REQUEST_BODY_EMPTY": ErrorStructDict(status_code=status.HTTP_400_BAD_REQUEST),
    }

    API_NOT_FOUND = "요청하신 경로를 찾을 수 없어요, 새로고침 후 다시 시도해주세요."
    RESOURCE_NOT_FOUND = "요청하신 정보를 찾을 수 없어요."
    JSON_DECODE_ERROR = "이해할 수 없는 유형의 데이터를 받았어요."

    REQUEST_TOO_FREQUENT = "요청이 너무 빈번해요, 조금 천천히 진행해주세요."
    REQUEST_BODY_EMPTY = "입력하신 정보가 서버에 전달되지 않았어요, 새로고침 후 다시 시도해주세요."
    REQUEST_BODY_LACK = "입력하신 정보 중 누락된 부분이 있어요, 다시 입력해주세요."
    REQUEST_BODY_INVALID = "입력하신 정보가 올바르지 않아요, 다시 입력해주세요."
    REQUEST_BODY_CONTAINS_INVALID_CHAR = "입력 불가능한 문자가 포함되어 있어요, 다시 입력해주세요."
