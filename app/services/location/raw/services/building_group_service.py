from app.services.location.raw.managers.building_group_manager import BuildingGroupManager
from app.services.location.raw.services.abstract_address_service import AbstractAddressService

class BuildingGroupService(AbstractAddressService):
    def __init__(self, manager: BuildingGroupManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_building_group'

    @property
    def manager(self) -> BuildingGroupManager:
        return self._manager