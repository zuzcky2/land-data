from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.price_info.price_info_dgk \
    import (PriceInfoDgkDriver)
from app.services.building.raw.drivers.price_info.price_info_mongodb \
    import (PriceInfoMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class PriceInfoManager(AbstractManager):
    _mongodb_driver: PriceInfoMongodbDriver
    _dgk_driver: PriceInfoDgkDriver

    def __init__(self, mongodb_driver: PriceInfoMongodbDriver, dgk_driver: PriceInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
