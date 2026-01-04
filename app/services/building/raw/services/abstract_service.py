from abc import abstractmethod, ABC
from typing import Optional, List, Any, Dict
from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.core.helpers.log import Log
import logging


class AbstractService(ABC):
    # 드라이버 이름 상수화
    DRIVER_MONGODB = 'mongodb'
    DRIVER_DGK = 'dgk'

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

    def sync_from_dgk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Sync Start: {params}")

        try:
            # 드라이버 호출 및 데이터 읽기
            dgk_pagination = (
                self.manager.driver(self.DRIVER_DGK)
                .clear()
                .set_arguments(params)
                .set_pagination(page=params.get('page', 1), per_page=params.get('per_page', 100))
                .read()
            )

            # PaginationDto 객체에서 total과 items 추출
            items = getattr(dgk_pagination, 'items', [])
            total = getattr(dgk_pagination, 'total', 0)

            if items:
                self.manager.driver(self.DRIVER_MONGODB).store(items)

            return {
                'total': total,
                'count': len(items),
                'page': getattr(dgk_pagination, 'page', 1),
                'status': 'success'
            }

        except Exception as e:
            # 에러 발생 시 상세 정보 로깅 (나중에 재개 프로그램이 읽을 포인트)
            error_msg = (
                f"[SYNC_STOP_ERROR] | Message: {str(e)} | "
                f"Params: sigunguCd={params.get('sigunguCd')}, "
                f"bjdongCd={params.get('bjdongCd')}, "
                f"page={params.get('page')}"
            )
            self.logger.error(error_msg)

            raise e