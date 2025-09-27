from fastapi import APIRouter
from src.routes.config_node import config_node_router
from src.routes.device import device_router
from src.routes.health_check import health_check_router
from src.routes.json_schema import json_schema_router

router = APIRouter()
router.include_router(health_check_router)
router.include_router(json_schema_router)
router.include_router(config_node_router)
router.include_router(device_router)
