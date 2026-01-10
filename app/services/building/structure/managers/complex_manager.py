from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.services.building.structure.drivers.complex.complex_mongodb_driver \
    import (ComplexMongodbDriver)
from app.services.building.structure.drivers.driver_interface \
    import (DriverInterface)


class ComplexManager(AbstractManager):
    _mongodb_driver: ComplexMongodbDriver

    def __init__(self, mongodb_driver: ComplexMongodbDriver):
        self._mongodb_driver = mongodb_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver
