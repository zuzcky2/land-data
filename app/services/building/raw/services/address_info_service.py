
from app.services.building.raw.managers.address_info_manager import AddressInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class AddressInfoService(AbstractService):

    def __init__(self, manager: AddressInfoManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'building_raw_address_info'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

