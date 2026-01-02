
from app.services.building.raw.managers.price_info_manager import PriceInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class PriceInfoService(AbstractService):

    def __init__(self, manager: PriceInfoManager):
        self._manager = manager

    @property
    def manager(self) -> AbstractManager:
        return self._manager

