from bson import ObjectId
from pydantic import Field
from typing import Optional, List
from app.services.contracts.dto import MongoModel
from datetime import datetime


class ComplexDto(MongoModel):
    building_manage_number: str = Field(None, title='건물관리번호 (25자리, bdMgtSn)')

    address_id: ObjectId = Field(title='address dto 객체의 id')
    item_name: str = Field(title='단지명 (건물명)')
    register_kind_code: str = Field(title='대장구분 (총괄표제부, 일반건축물, 표제부)')
    register_manage_number: str = Field(title='총괄표제부, 일반건축물, 표제부의 PK')

    # 규모 및 면적
    land_area: float = Field(title='대지면적')
    building_area: float = Field(title='건축면적 (하늘에서 보았을 때 건물이 차지하는 수평 투영 면적)')
    total_floor_area: float = Field(title='연면적 (지하층을 포함한 모든 층의 바닥 면적 합계)')
    building_coverage_ratio: float = Field(title='건폐율 (대지면적에 대한 건축면적의 비율)')
    floor_area_ratio: float = Field(title='용적률 (대지면적에 대한 지상층 연면적의 비율)')
    main_building_count: int = Field(1, title='단지 내 주된 건물의 동 수')
    annex_building_count: int = Field(0, title='경비실, 기계실 등 부속 건물 수')

    # 세대 및 가구
    household_count: Optional[int] = Field(None, title='공동주택의 세대수')
    family_count: Optional[int] = Field(None, title='단독, 다가구 주택의 거주 단위 수')
    unit_count: Optional[int] = Field(None, title='상가, 오피스텔 등 개별 점포/호실 수')
    display_count: Optional[int] = Field(None, title='용도에 해당하는 표기 세대수')

    # 주차 정보
    total_parking_count: Optional[int] = Field(None, title='단지 내 전체 주차 가능 대수')
    indoor_parking_count: Optional[int] = Field(None, title='건물 내부 자주식 주차 대수')
    outdoor_parking_count: Optional[int] = Field(None, title='건물 외부 자주식 주차 대수')

    # 카테고리 정보 (단수 & 복수)
    main_category: str = Field(title='대표 1차 카테고리')
    sub_category: str = Field(title='대표 2차 카테고리')
    category_tags: List[str] = Field(default_factory=list, title='1차 카테고리 태그 리스트')
    sub_category_tags: List[str] = Field(default_factory=list, title='2차 카테고리 태그 리스트')

    # 날짜 정보
    permit_date: Optional[datetime] = Field(None, title='건축 허가를 받은 날짜')
    construction_date: Optional[datetime] = Field(None, title='실제 공사를 시작한 날짜')
    approval_date: Optional[datetime] = Field(None, title='중공 후 사용이 승인된 날짜 (실제 나이)')
    display_date_name: Optional[str] = Field(None, title='노출 가능한 날짜정보 (우선순위: 사용승인일, 착공일, 허가일)')
    display_date: Optional[datetime] = Field(None, title='노출 가능한 날짜 값')

    # 인허가 정보
    permit_authority: Optional[str] = Field(None, title='인허가를 담당한 기관/부서명')
    permit_year: Optional[datetime] = Field(None, title='건축 허가가 난 연도')


