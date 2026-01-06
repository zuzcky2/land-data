
from app.services.building.raw.managers.relation_info_manager import RelationInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class RelationInfoService(AbstractService):

    def __init__(self, manager: RelationInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_relation_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

