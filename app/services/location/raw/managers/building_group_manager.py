from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.building_group.building_group_text_driver \
    import (BuildingGroupTextDriver)
from app.services.location.raw.drivers.building_group.building_group_mongodb_driver \
    import (BuildingGroupMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class BuildingGroupManager(AbstractManager):
    _text_driver: BuildingGroupTextDriver
    _mongodb_driver: BuildingGroupMongodbDriver

    def __init__(self, mongodb_driver: BuildingGroupMongodbDriver, text_driver: BuildingGroupTextDriver):
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