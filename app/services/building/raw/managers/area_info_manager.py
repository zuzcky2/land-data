from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.area_info.area_info_mongodb \
    import (AreaInfoMongodbDriver)
from app.services.building.raw.drivers.area_info.area_info_dgk \
    import (AreaInfoDgkDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class AreaInfoManager(AbstractManager):
    _mongodb_driver: AreaInfoMongodbDriver
    _dgk_driver: AreaInfoDgkDriver

    def __init__(self, mongodb_driver: AreaInfoMongodbDriver, dgk_driver: AreaInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
