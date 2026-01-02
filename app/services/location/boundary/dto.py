from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Generic
from datetime import datetime
from app.services.location.boundary.types.boundary import LEGAL, STATE, DISTRICT, TOWNSHIP, VILLAGE, GeoJSONType
from app.services.contracts.dto import PaginationDto, T, MongoModel

class BoundaryItemDto(MongoModel):
    """
    단일 지역 항목에 대한 데이터 전송 객체 (DTO)입니다.
    """

    item_code: str = Field(..., min_length=2, max_length=10, title='지역 코드')
    item_name: str = Field(..., title='지역명')
    item_full_name: str = Field(..., title='전체 지역명')
    short_name: Optional[str] = Field(None, title='짧은 지역명')
    location_type: Literal[STATE, DISTRICT, TOWNSHIP, VILLAGE] = Field(..., title='지역 유형')
    state_code: str = Field(..., min_length=2, max_length=2, title='시도 코드')
    district_code: Optional[str] = Field(None, min_length=5, max_length=5, title='시군구 코드')
    township_code: Optional[str] = Field(None, min_length=8, max_length=8, title='읍면동 코드')
    village_code: Optional[str] = Field(None, min_length=10, max_length=10, title='리 코드')
    jurisdiction_type: Literal[LEGAL] = Field(..., title='구역 유형')
    bbox: List[float] = Field(..., title='구역 범위 위경도')
    geo_point: GeoJSONType = Field(..., title='구역 중앙 geoJson')
    geo_polygon: Optional[GeoJSONType] = Field(None, title='구역 위경도 폴리곤 geoJson')
    last_updated_at: Optional[datetime] = Field(None, title='API 최근 수정일')
    created_at: datetime = Field(default_factory=datetime.now, title='생성일')
    updated_at: datetime = Field(default_factory=datetime.now, title='수정일')
    deleted_at: Optional[datetime] = Field(None, title='삭제일')
    manual_order: Optional[int] = Field(None, title='매뉴얼 정렬 순서')

# 핵심 수정: PaginationDto[T]를 상속받고 Generic[T]를 명시합니다.
class BoundaryPaginationDto(PaginationDto[T], Generic[T]):
    """
    페이지네이션된 지역 항목 목록에 대한 데이터 전송 객체 (DTO)입니다.
    """
    # 1. 부모 클래스에 이미 page, per_page, total, items 등이 있으므로 중복 선언 불필요
    # 2. 만약 자식에서 items의 title 등을 수정하고 싶다면 반드시 List[T]를 유지해야 함
    items: List[T] = Field(default_factory=list, title='지역 경계 아이템 목록')

# 외부로 노출할 클래스 정의
__all__ = ['BoundaryItemDto', 'BoundaryPaginationDto']