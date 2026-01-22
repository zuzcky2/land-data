from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.kapt_basic.kapt_basic_dgk_driver \
    import (KaptBasicDgkDriver)
from app.services.building.raw.drivers.kapt_basic.kapt_basic_mongodb \
    import (KaptBasicMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class KaptBasicManager(AbstractManager):
    _mongodb_driver: KaptBasicMongodbDriver
    _dgk_driver: KaptBasicDgkDriver

    def __init__(self, mongodb_driver: KaptBasicMongodbDriver, dgk_driver: KaptBasicDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
