from abc import ABC, abstractmethod
from typing import Optional
from app.services.building.raw.drivers.driver_interface import DriverInterface
from app.services.contracts.manager import AbstractManager as ContractAbstractManager


class AbstractManager(ContractAbstractManager, ABC):

    @property
    @abstractmethod
    def mongodb_driver(self) -> DriverInterface:
        pass

    @property
    @abstractmethod
    def dgk_driver(self) -> DriverInterface:
        pass

    def get_default_driver(self) -> str:
        return 'mongodb'

    def driver(self, name: Optional[str] = None) -> DriverInterface:
        return super().driver(name)

    def _create_mongodb_driver(self) -> DriverInterface:
        return self.mongodb_driver

    def _create_dgk_driver(self) -> DriverInterface:
        return self.dgk_driver