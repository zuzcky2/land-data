from abc import ABC, abstractmethod
from typing import Optional
from app.services.message.webhook.drivers.driver_interface import DriverInterface
from app.services.contracts.manager import AbstractManager as ContractAbstractManager


class AbstractManager(ContractAbstractManager, ABC):

    @property
    @abstractmethod
    def default_driver(self) -> DriverInterface:
        pass

    def get_default_driver(self) -> str:
        return 'default'

    def driver(self, name: Optional[str] = None) -> DriverInterface:
        return super().driver(name)

    def _create_default_driver(self) -> DriverInterface:
        return self.default_driver
