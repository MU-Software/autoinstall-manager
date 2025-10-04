from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import Device
from src.repositories import EnumValue
from src.repositories.device import deviceRepoDI

device_router = APIRouter(prefix="/device", tags=[OpenAPITag.DEVICE])


@device_router.get("/", response_model=Sequence[Device])
async def list_devices(device_repo: deviceRepoDI) -> Sequence[Device]:
    return await device_repo.list()


@device_router.get("/enum-values", response_model=Sequence[EnumValue])
async def list_device_enum_values(device_repo: deviceRepoDI) -> Sequence[EnumValue]:
    return await device_repo.list_enum_values()


@device_router.get("/{device_id}", response_model=Device)
async def retrieve_device(device_id: UUID, device_repo: deviceRepoDI) -> Device:
    return await device_repo.retrieve_by_id(id=device_id)
