from typing import Optional

from app.services.contracts.manager import AbstractManager
from app.services.location.boundary.drivers.mongodb import MongoDBDriver
from app.services.location.boundary.drivers.vworld import VWorldDriver
from app.services.location.boundary.drivers.interface import BoundaryInterface


class BoundaryManager(AbstractManager):
    mongodb_driver: MongoDBDriver
    vworld_driver: VWorldDriver

    def __init__(self, mongodb_driver: MongoDBDriver, vworld_driver: VWorldDriver):
        self.mongodb_driver = mongodb_driver
        self.vworld_driver = vworld_driver

    def get_default_driver(self) -> str:
        return 'mongodb'

    def driver(self, name: Optional[str] = None) -> BoundaryInterface:
        return super().driver(name)

    def _create_mongodb_driver(self) -> MongoDBDriver:
        return self.mongodb_driver

    def _create_vworld_driver(self) -> VWorldDriver:
        return self.vworld_driver

