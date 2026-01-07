from abc import abstractmethod, ABC
from typing import Optional, List, Any, Dict
from datetime import datetime, timedelta, timezone

import bson.objectid

from app.services.contracts.dto import PaginationDto
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.core.helpers.log import Log
import logging


class AbstractService(ABC):
    # 드라이버 이름 상수화
    DRIVER_MONGODB = 'mongodb'
    DRIVER_JGK = 'jgk'
    DRIVER_VWORLD = 'vworld'

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

    def get_list(self, params: Dict[str, Any], driver_name: Optional[str] = None) -> PaginationDto[dict]:
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

    def is_expired(self, _id: bson.objectid.ObjectId, days_limit):
        """
        item의 생성일이 입력받은 days_limit(일수)보다 오래되었는지 체크
        """
        # 1. ObjectId에서 생성 시간 추출 (UTC)
        created_at = _id.generation_time

        # 2. 현재 시간 가져오기 (UTC)
        now = datetime.now(timezone.utc)

        # 3. 기준일(days_limit)만큼 차이 계산
        time_diff = now - created_at

        # 4. 차이가 기준일보다 크면 만료(True)로 판단
        return time_diff.days >= days_limit