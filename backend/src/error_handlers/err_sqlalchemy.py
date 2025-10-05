from __future__ import annotations

from collections.abc import Callable, Coroutine
from re import Match
from typing import Any

from psycopg.errors import (
    AdminShutdown,
    CannotConnectNow,
    CheckViolation,
    ConfigFileError,
    CrashShutdown,
    DatabaseDropped,
    DatabaseError,
    DataCorrupted,
    DataError,
    DiskFull,
    DuplicateFile,
)
from psycopg.errors import Error as PsycopgError
from psycopg.errors import (
    ExclusionViolation,
    ForeignKeyViolation,
    IndexCorrupted,
    IntegrityConstraintViolation,
    IntegrityError,
    InterfaceError,
    InvalidPassword,
    IoError,
    NotNullViolation,
    OutOfMemory,
    RestrictViolation,
    SystemError,
    TooManyArguments,
    TooManyColumns,
    UndefinedFile,
    UniqueViolation,
)
from sqlalchemy.exc import SQLAlchemyError
from src.consts.errors import DBServerError, DBValueError, ErrorEnum
from src.models import NAMING_CONVENTION_DICT, NCKeyType
from starlette.requests import Request
from starlette.responses import JSONResponse

IntegrityErrorMsgMap: dict[NCKeyType, ErrorEnum] = {
    "ix": DBServerError.DB_INTEGRITY_CONSTRAINT_ERROR,
    "uq": DBValueError.DB_UNIQUE_CONSTRAINT_ERROR,
    "ck": DBValueError.DB_CHECK_CONSTRAINT_ERROR,
    "fk": DBValueError.DB_FOREIGN_KEY_CONSTRAINT_ERROR,
    "pk": DBValueError.DB_NOT_NULL_CONSTRAINT_ERROR,
}


def error_to_nckey(
    msg_primary: str | None,
) -> tuple[NCKeyType, Match] | tuple[None, None]:
    if not isinstance(msg_primary, str):
        return None, None
    for nckey, ncdef in NAMING_CONVENTION_DICT.items():
        if matched_info := ncdef.regex.match(msg_primary):
            return nckey, matched_info
    return None, None


async def psycopg_dataerror_handler(req: Request, err: DataError) -> JSONResponse:
    # TODO: FIXME: THis sould be handled by RepositoryImpl or CRUDView.
    # [print(attr, getattr(err.diag, attr)) for attr in dir(err.diag) if not attr.startswith("_")]
    return DBValueError.DB_DATA_ERROR.response()


async def psycopg_integrityerror_handler(req: Request, err: IntegrityError) -> JSONResponse:
    # TODO: FIXME: THis sould be handled by RepositoryImpl.
    match err:
        case IntegrityConstraintViolation():
            return DBServerError.DB_INTEGRITY_CONSTRAINT_ERROR.response()
        case RestrictViolation():
            return DBValueError.DB_RESTRICT_CONSTRAINT_ERROR.response()
        case NotNullViolation():
            if err.diag.column_name:
                return DBValueError.DB_NOT_NULL_CONSTRAINT_ERROR(loc=[err.diag.column_name]).response()
            return DBValueError.DB_NOT_NULL_CONSTRAINT_ERROR.response()
        case ForeignKeyViolation():
            return DBValueError.DB_NOT_NULL_CONSTRAINT_ERROR.format_msg(referred_table_name=err.diag.table_name or "").response()
        case UniqueViolation():
            return DBValueError.DB_UNIQUE_CONSTRAINT_ERROR.response()
        case CheckViolation():
            return DBValueError.DB_CHECK_CONSTRAINT_ERROR.response()
        case ExclusionViolation():
            return DBValueError.DB_EXCLUSION_CONSTRAINT_ERROR.response()
        case _:
            nc_key, _ = error_to_nckey(err.diag.message_primary)
            if not nc_key:
                return DBServerError.DB_UNKNOWN_ERROR.response()
            return IntegrityErrorMsgMap.get(nc_key, DBServerError.DB_UNKNOWN_ERROR()).response()


async def psycopg_databaseerror_handler(req: Request, err: DatabaseError) -> JSONResponse:
    if handler_func := error_handler_patterns.get(type(err)):
        return await handler_func(req, err)
    return DBServerError.DB_UNKNOWN_ERROR.response()


async def psycopg_interfaceerror_handler(req: Request, err: PsycopgError) -> JSONResponse:
    return DBServerError.DB_INTERFACE_ERROR.response()


async def psycopg_connectionerror_handler(req: Request, err: PsycopgError) -> JSONResponse:
    return DBServerError.DB_CONNECTION_ERROR.response()


async def psycopg_criticalerror_handler(req: Request, err: PsycopgError) -> JSONResponse:
    return DBServerError.DB_CRITICAL_ERROR.response()


async def sqlalchemy_error_handler(req: Request, err: SQLAlchemyError) -> JSONResponse:
    orig_exception: PsycopgError | BaseException | None  # For sqlalchemy.exc.IntegrityError
    if orig_exception := getattr(err, "orig", None):
        for orig_err_type in type(orig_exception).__mro__:
            if handler_func := error_handler_patterns.get(orig_err_type):
                return await handler_func(req, orig_exception)
    return DBServerError.DB_UNKNOWN_ERROR.response()


# TODO: Delete type: ignore mypy errors.
error_handler_patterns: dict[
    type[PsycopgError | SQLAlchemyError], Callable[[Request, PsycopgError | SQLAlchemyError], Coroutine[Any, Any, JSONResponse]]
] = {
    # PostgreSQL Connection Error
    InterfaceError: psycopg_interfaceerror_handler,  # type: ignore[dict-item]
    CannotConnectNow: psycopg_connectionerror_handler,  # type: ignore[dict-item]
    # PostgreSQL Critical Error
    DataCorrupted: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    IndexCorrupted: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    DiskFull: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    OutOfMemory: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    TooManyArguments: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    TooManyColumns: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    ConfigFileError: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    InvalidPassword: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    AdminShutdown: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    CrashShutdown: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    DatabaseDropped: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    SystemError: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    IoError: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    UndefinedFile: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    DuplicateFile: psycopg_criticalerror_handler,  # type: ignore[dict-item]
    # PostgreSQL Integrity Error
    IntegrityConstraintViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    RestrictViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    NotNullViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    ForeignKeyViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    UniqueViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    CheckViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    ExclusionViolation: psycopg_integrityerror_handler,  # type: ignore[dict-item]
    # PostgreSQL Data Error
    DataError: psycopg_dataerror_handler,  # type: ignore[dict-item]
    # PostgreSQL Database Error
    PsycopgError: psycopg_databaseerror_handler,  # type: ignore[dict-item]
    # SQLAlchemy Error
    SQLAlchemyError: sqlalchemy_error_handler,  # type: ignore[dict-item]
}
