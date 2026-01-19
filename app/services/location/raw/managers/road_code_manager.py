from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.road_code.road_code_text_driver \
    import (RoadCodeTextDriver)
from app.services.location.raw.drivers.road_code.road_code_mongodb_driver \
    import (RoadCodeMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class RoadCodeManager(AbstractManager):
    _text_driver: RoadCodeTextDriver
    _mongodb_driver: RoadCodeMongodbDriver

    def __init__(self, mongodb_driver: RoadCodeMongodbDriver, text_driver: RoadCodeTextDriver):
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