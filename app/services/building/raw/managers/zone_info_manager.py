from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.zone_info.zone_info_dgk \
    import (ZoneInfoDgkDriver)
from app.services.building.raw.drivers.zone_info.zone_info_mongodb \
    import (ZoneInfoMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class ZoneInfoManager(AbstractManager):
    _mongodb_driver: ZoneInfoMongodbDriver
    _dgk_driver: ZoneInfoDgkDriver

    def __init__(self, mongodb_driver: ZoneInfoMongodbDriver, dgk_driver: ZoneInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
