from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.address_info.address_info_dgk \
    import (AddressInfoDgkDriver)
from app.services.building.raw.drivers.address_info.address_info_mongodb \
    import (AddressInfoMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class AddressInfoManager(AbstractManager):
    _mongodb_driver: AddressInfoMongodbDriver
    _dgk_driver: AddressInfoDgkDriver

    def __init__(self, mongodb_driver: AddressInfoMongodbDriver, dgk_driver: AddressInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
