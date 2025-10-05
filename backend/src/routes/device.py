from collections.abc import Sequence
from uuid import UUID

from fastapi import APIRouter
from src.consts.tags import OpenAPITag
from src.models import Device
from src.schemas.enum_value import EnumValue
from src.schemas.list_value import ListValue
from src.services.device import deviceServiceDI

device_router = APIRouter(prefix="/device", tags=[OpenAPITag.DEVICE])


@device_router.get("/", response_model=Sequence[ListValue])
async def list_devices(device_svc: deviceServiceDI) -> Sequence[ListValue]:
    return await device_svc.list_values()


@device_router.get("/enum-values", response_model=Sequence[EnumValue])
async def list_device_enum_values(device_svc: deviceServiceDI) -> Sequence[EnumValue]:
    return await device_svc.list_enum_values()


@device_router.get("/{device_id}", response_model=Device)
async def retrieve_device(device_id: UUID, device_svc: deviceServiceDI) -> Device:
    return await device_svc.retrieve_by_id(id=device_id)


@device_router.post("/", response_model=Device)
async def create_device(device: Device, device_svc: deviceServiceDI) -> Device:
    return await device_svc.create(obj=device)


@device_router.put("/", response_model=Device)
async def update_device(device: Device, device_svc: deviceServiceDI) -> Device:
    return await device_svc.update(obj=device)


@device_router.delete("/{device_id}", response_model=None)
async def delete_device(device_id: UUID, device_svc: deviceServiceDI) -> None:
    await device_svc.delete_by_id(id=device_id)
