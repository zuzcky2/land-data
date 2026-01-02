from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.basic_info.basic_info_mongodb \
    import (BasicInfoMongodbDriver)
from app.services.building.raw.drivers.basic_info.basic_info_dgk \
    import (BasicInfoDgkDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class BasicInfoManager(AbstractManager):
    _mongodb_driver: BasicInfoMongodbDriver
    _dgk_driver: BasicInfoDgkDriver

    def __init__(self, mongodb_driver: BasicInfoMongodbDriver, dgk_driver: BasicInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
