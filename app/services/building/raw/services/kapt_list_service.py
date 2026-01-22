
from app.services.building.raw.managers.kapt_list_manager import KaptListManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class KaptListService(AbstractService):

    def __init__(self, manager: KaptListManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_kapt_list'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

