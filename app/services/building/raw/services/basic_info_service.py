# app/services/building/raw/basic_info_service.py

from app.services.building.raw.managers.basic_info_manager import BasicInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class BasicInfoService(AbstractService):

    def __init__(self, manager: BasicInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_basic_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

