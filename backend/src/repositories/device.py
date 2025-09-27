from typing import Annotated

from fastapi import Depends
from src.models import Device
from src.repositories import RepositoryImpl


class DeviceRepository(RepositoryImpl[Device]):
    model = Device


deviceRepoDI = Annotated[DeviceRepository, Depends(DeviceRepository)]
