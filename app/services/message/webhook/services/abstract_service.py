from abc import abstractmethod, ABC
from typing import Optional, List, Any, Dict
from app.services.message.webhook.managers.abstract_manager import AbstractManager
from app.core.helpers.log import Log
import logging


class AbstractService(ABC):
    @property
    @abstractmethod
    def logger_name(self) -> str:
        return 'default'

    @property
    def logger(self) -> logging.Logger:
        return Log.get_logger(self.logger_name)

    @property
    @abstractmethod
    def manager(self) -> AbstractManager:
        pass
