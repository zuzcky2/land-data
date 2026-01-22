
from app.services.building.raw.managers.kapt_detail_manager import KaptDetailManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class KaptDetailService(AbstractService):

    def __init__(self, manager: KaptDetailManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_kapt_detail'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

