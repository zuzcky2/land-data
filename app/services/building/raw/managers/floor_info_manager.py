from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.floor_info.floor_info_mongodb \
    import (FloorInfoMongodbDriver)
from app.services.building.raw.drivers.floor_info.floor_info_dgk \
    import (FloorInfoDgkDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class FloorInfoManager(AbstractManager):
    _mongodb_driver: FloorInfoMongodbDriver
    _dgk_driver: FloorInfoDgkDriver

    def __init__(self, mongodb_driver: FloorInfoMongodbDriver, dgk_driver: FloorInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver


