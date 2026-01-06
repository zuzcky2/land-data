
from app.services.building.raw.managers.group_info_manager import GroupInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class GroupInfoService(AbstractService):

    def __init__(self, manager: GroupInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_group_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

