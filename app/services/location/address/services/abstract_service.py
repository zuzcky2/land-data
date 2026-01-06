from abc import abstractmethod, ABC
from typing import Optional, List, Any, Dict
from app.services.location.address.managers.abstract_manager import AbstractManager
from app.core.helpers.log import Log
import logging


class AbstractService(ABC):
    # 드라이버 이름 상수화
    DRIVER_MONGODB = 'mongodb'
    DRIVER_JGK = 'jgk'

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

    def sync_from_jgk(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        # 소스별로 다른 로거 사용 (building_raw_group, building_raw_title)
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            item = (
                self.manager.driver(self.DRIVER_JGK)
                .clear()
                .set_arguments(params)
                .set_pagination(page=1, per_page=1)
                .read_one()
            )

            if item:
                self.manager.driver(self.DRIVER_MONGODB).store([item])
                return {'status': 'success', 'bdMgtSn': item.get('bdMgtSn')}
            else:
                return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {str(params)}")
            raise e