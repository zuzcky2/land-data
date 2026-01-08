from abc import abstractmethod, ABC
from typing import Optional, List, Any, Dict
from app.services.building.structure.managers.abstract_manager import AbstractManager
from app.core.helpers.log import Log
import logging


class AbstractService(ABC):
    @property
    @abstractmethod
    def logger_name(self) -> str:
        return 'building_raw'

    @property
    def logger(self) -> logging.Logger:
        return Log.get_logger(self.logger_name)

    @property
    @abstractmethod
    def manager(self) -> AbstractManager:
        pass

    def get_list(self, params: Dict[str, Any], driver_name: Optional[str] = None) -> Dict[str, Any]:
        """
        건축물대장 표제부 목록을 페이징 조회합니다. (기본: MongoDB)
        """
        page = int(params.get('page', 1))
        per_page = int(params.get('per_page', 20))

        driver = self.manager.driver(driver_name)

        return (
            driver.clear()
            .set_arguments(params)
            .set_pagination(page=page, per_page=per_page)
            .read()
        )

    def get_detail(self, params: Dict[str, Any], driver_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        단일 건축물대장 데이터를 조회합니다.
        """
        return (
            self.manager.driver(driver_name)
            .clear()
            .set_arguments(params)
            .read_one()
        )
