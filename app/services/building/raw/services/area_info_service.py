
from app.services.building.raw.managers.area_info_manager import AreaInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class AreaInfoService(AbstractService):

    def __init__(self, manager: AreaInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_area_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

