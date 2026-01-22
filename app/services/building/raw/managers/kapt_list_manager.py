from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.kapt_list.kapt_list_dgk_driver \
    import (KaptListDgkDriver)
from app.services.building.raw.drivers.kapt_list.kapt_list_mongodb \
    import (KaptListMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class KaptListManager(AbstractManager):
    _mongodb_driver: KaptListMongodbDriver
    _dgk_driver: KaptListDgkDriver

    def __init__(self, mongodb_driver: KaptListMongodbDriver, dgk_driver: KaptListDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
