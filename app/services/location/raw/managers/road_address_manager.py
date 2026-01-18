from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.road_address.road_address_text_driver \
    import (RoadAddressTextDriver)
from app.services.location.raw.drivers.road_address.road_address_mongodb_driver \
    import (RoadAddressMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class RoadAddressManager(AbstractManager):
    _text_driver: RoadAddressTextDriver
    _mongodb_driver: RoadAddressMongodbDriver

    def __init__(self, mongodb_driver: RoadAddressMongodbDriver, text_driver: RoadAddressTextDriver):
        self._mongodb_driver = mongodb_driver
        self._text_driver = text_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def text_driver(self) -> DriverInterface:
        return self._text_driver

    def _create_text_driver(self) -> DriverInterface:
        return self.text_driver