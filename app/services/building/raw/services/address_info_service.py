
from app.services.building.raw.managers.address_info_manager import AddressInfoManager
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.services.abstract_service import AbstractService


class AddressInfoService(AbstractService):

    def __init__(self, manager: AddressInfoManager):
        self._manager = manager

    @property
    def manager(self) -> AbstractManager:
        return self._manager

