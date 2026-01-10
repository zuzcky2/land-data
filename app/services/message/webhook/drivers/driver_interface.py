from abc import ABC, abstractmethod
from typing import List, Optional, Any

from app.services.contracts.drivers.abstract import AbstractDriver


class DriverInterface(AbstractDriver, ABC):
    @abstractmethod
    def post(self, items: List[dict]) -> Any:
        """데이터를 저장소에 저장합니다."""
        pass