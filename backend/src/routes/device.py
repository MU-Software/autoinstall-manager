from fastapi import APIRouter
from src.consts.tags import OpenAPITag

device_router = APIRouter(prefix="/devices", tags=[OpenAPITag.DEVICE])

"""
endpoint 목록
- device list / retrieve / create / update / delete
"""
