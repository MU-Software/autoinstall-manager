from typing import Annotated

from fastapi import Depends
from src.models import Device
from src.repositories.device import deviceRepoDI
from src.services import ServiceImpl


class DeviceService(ServiceImpl[Device]):
    repository: deviceRepoDI


deviceServiceDI = Annotated[DeviceService, Depends(DeviceService)]
