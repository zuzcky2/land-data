
from app.services.building.raw.managers.zone_info_manager import ZoneInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class ZoneInfoService(AbstractService):

    def __init__(self, manager: ZoneInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_relation_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

