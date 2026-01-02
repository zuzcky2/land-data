# app/services/building/raw/title_info_service.py

from app.services.building.raw.managers.title_info_manager import TitleInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class TitleInfoService(AbstractService):

    def __init__(self, manager: TitleInfoManager):
        self._manager = manager

    @property
    def manager(self) -> AbstractManager:
        return self._manager

