from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.services.building.structure.drivers.floor.floor_mongodb_driver import FloorMongodbDriver
from app.services.building.structure.drivers.driver_interface import DriverInterface


class FloorManager(AbstractManager):
    _mongodb_driver: FloorMongodbDriver

    def __init__(self, mongodb_driver: FloorMongodbDriver):
        self._mongodb_driver = mongodb_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver
