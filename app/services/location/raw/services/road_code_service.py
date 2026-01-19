from app.services.location.raw.managers.road_address_manager import RoadAddressManager
from app.services.location.raw.services.abstract_address_service import AbstractAddressService

class RoadCodeService(AbstractAddressService):
    def __init__(self, manager: RoadAddressManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_road_code'

    @property
    def manager(self) -> RoadAddressManager:
        return self._manager