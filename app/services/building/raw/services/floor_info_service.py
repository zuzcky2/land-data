# app/services/building/raw/floor_info_service.py

from app.services.building.raw.managers.floor_info_manager import FloorInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class FloorInfoService(AbstractService):

    def __init__(self, manager: FloorInfoManager):
        self._manager = manager

    @property
    def manager(self) -> AbstractManager:
        return self._manager

