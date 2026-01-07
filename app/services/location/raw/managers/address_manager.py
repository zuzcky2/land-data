from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.address.address_jgk_driver \
    import (AddressJgkDriver)
from app.services.location.raw.drivers.address.address_mongodb_driver \
    import (AddressMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class AddressManager(AbstractManager):
    _jgk_driver: AddressJgkDriver
    _mongodb_driver: AddressMongodbDriver

    def __init__(self, mongodb_driver: AddressMongodbDriver, jgk_driver: AddressJgkDriver):
        self._mongodb_driver = mongodb_driver
        self._jgk_driver = jgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def jgk_driver(self) -> DriverInterface:
        return self._jgk_driver

    def _create_jgk_driver(self) -> DriverInterface:
        return self.jgk_driver