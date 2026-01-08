from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.services.building.structure.drivers.address.address_mongodb_driver \
    import (AddressMongodbDriver)
from app.services.building.structure.drivers.driver_interface \
    import (DriverInterface)


class AddressManager(AbstractManager):
    _mongodb_driver: AddressMongodbDriver

    def __init__(self, mongodb_driver: AddressMongodbDriver):
        self._mongodb_driver = mongodb_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver
