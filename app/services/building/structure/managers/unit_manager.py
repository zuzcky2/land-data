from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.services.building.structure.drivers.unit.unit_mongodb_driver import UnitMongodbDriver
from app.services.building.structure.drivers.driver_interface import DriverInterface


class UnitManager(AbstractManager):
    _mongodb_driver: UnitMongodbDriver

    def __init__(self, mongodb_driver: UnitMongodbDriver):
        self._mongodb_driver = mongodb_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver
