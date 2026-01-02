from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from app.services.location.boundary.dto import BoundaryItemDto, BoundaryPaginationDto
from pydantic import BaseModel, Field
from app.services.contracts.drivers.abstract import AbstractDriver  # 부모 클래스 임포트
from app.services.location.boundary.handlers.build_boundary_item_handler import BuildBoundaryItemHandler


class BoundaryStoreResult(BaseModel):
    """드라이버 공통 저장 결과 객체"""
    success: bool = Field(True, description="작업 성공 여부")
    matched_count: int = Field(0, description="조건에 일치한 문서 수")
    modified_count: int = Field(0, description="수정된 문서 수")
    upserted_count: int = Field(0, description="새로 삽입(upsert)된 문서 수")
    raw_response: Optional[Any] = Field(None, description="드라이버별 원본 응답 데이터 (디버깅용)")


class BoundaryInterface(AbstractDriver, ABC):
    item_type = BoundaryItemDto

    @abstractmethod
    def _fetch_raw(self, single: bool = False) -> List[BoundaryItemDto]:
        """
        각 드라이버는 이 메서드에서 반드시 BoundaryItemDto 객체의 리스트를 반환해야 합니다.
        변환 로직(핸들러 등)이 필요하다면 이 메서드 내부에서 처리합니다.
        """
        pass

    @abstractmethod
    def _get_total_count(self) -> int:
        pass

    def read(self) -> Any:
        # 드라이버가 이미 DTO로 변환해서 준다고 믿고 페이징만 입힙니다.
        items = self._fetch_raw(single=False)
        total = self._get_total_count()

        return self.build_pagination(items=items, total=total)

    def read_one(self) -> Optional[BoundaryItemDto]:
        items = self._fetch_raw(single=True)
        return items[0] if items else None

    @abstractmethod
    def store(self, items: List[BoundaryItemDto]):
        pass

__all__=['BoundaryInterface']