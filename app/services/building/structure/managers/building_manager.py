from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.services.building.structure.drivers.building.building_mongodb_driver import BuildingMongodbDriver
from app.services.building.structure.drivers.driver_interface import DriverInterface


class BuildingManager(AbstractManager):
    _mongodb_driver: BuildingMongodbDriver

    def __init__(self, mongodb_driver: BuildingMongodbDriver):
        self._mongodb_driver = mongodb_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver
