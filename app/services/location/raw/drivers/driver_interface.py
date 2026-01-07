from abc import ABC, abstractmethod
from typing import List, Optional, Any

from app.services.contracts.drivers.abstract import AbstractDriver


class DriverInterface(AbstractDriver, ABC):
    @abstractmethod
    def _fetch_raw(self, single: bool = False) -> List[dict]:
        """데이터 소스(API 또는 DB)로부터 원본 dict 리스트를 가져옵니다."""
        pass

    @abstractmethod
    def _get_total_count(self) -> int:
        """조건에 맞는 전체 아이템 수를 반환합니다."""
        pass

    def read(self) -> dict:
        """목록 조회 및 페이징 처리된 결과를 반환합니다."""
        items = self._fetch_raw(single=False)
        total = self._get_total_count()

        # AbstractDriver의 build_pagination을 활용하여 반환
        return self.build_pagination(items=items, total=total)

    def read_one(self) -> Optional[dict]:
        """단일 항목을 조회합니다."""
        items = self._fetch_raw(single=True)
        return items[0] if items else None

    @abstractmethod
    def store(self, items: List[dict]) -> Any:
        """데이터를 저장소에 저장합니다."""
        pass