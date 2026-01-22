from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.kapt_detail.kapt_detail_dgk_driver \
    import (KaptDetailDgkDriver)
from app.services.building.raw.drivers.kapt_detail.kapt_detail_mongodb \
    import (KaptDetailMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class KaptDetailManager(AbstractManager):
    _mongodb_driver: KaptDetailMongodbDriver
    _dgk_driver: KaptDetailDgkDriver

    def __init__(self, mongodb_driver: KaptDetailMongodbDriver, dgk_driver: KaptDetailDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
