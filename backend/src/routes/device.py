from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import Device
from src.schemas.enum_value import EnumValue
from src.services.device import deviceServiceDI

device_router = APIRouter(prefix="/device", tags=[OpenAPITag.DEVICE])


@device_router.get("/", response_model=Sequence[Device])
async def list_devices(device_svc: deviceServiceDI) -> Sequence[Device]:
    return await device_svc.list()


@device_router.get("/enum-values", response_model=Sequence[EnumValue])
async def list_device_enum_values(device_svc: deviceServiceDI) -> Sequence[EnumValue]:
    return await device_svc.list_enum_values()


@device_router.get("/{device_id}", response_model=Device)
async def retrieve_device(device_id: UUID, device_svc: deviceServiceDI) -> Device:
    return await device_svc.retrieve_by_id(id=device_id)
