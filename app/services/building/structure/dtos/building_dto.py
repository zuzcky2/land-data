from pydantic import Field
from typing import Optional, List
from app.services.contracts.dto import MongoModel
from datetime import datetime


class BuildingDto(MongoModel):
    register_manage_number: str = Field(title='표제부 mgmBldrgstPk — PK')
    building_manage_number: str = Field(title='건물관리번호 (25자리, bdMgtSn) → complexes 참조')

    dong_name: Optional[str] = Field(None, title='동명 (예: 101동, A동)')
    main_purpose: Optional[str] = Field(None, title='주용도')
    sub_purpose: Optional[str] = Field(None, title='기타용도')
    structure: Optional[str] = Field(None, title='구조 (예: 철근콘크리트구조)')
    roof: Optional[str] = Field(None, title='지붕 (예: 철근콘크리트)')

    ground_floor_count: int = Field(0, title='지상 층수')
    underground_floor_count: int = Field(0, title='지하 층수')
    height: Optional[float] = Field(None, title='높이 (m)')

    total_area: float = Field(0.0, title='연면적 (㎡)')
    building_area: float = Field(0.0, title='건축면적 (㎡)')
    annex_area: float = Field(0.0, title='부속 건물 면적 합계')

    household_count: int = Field(0, title='세대수')
    family_count: int = Field(0, title='가구수')
    unit_count: int = Field(0, title='호실수 (상가/오피스텔)')

    is_main_building: bool = Field(True, title='주건축물 여부 (False이면 부속건물)')

    permit_date: Optional[datetime] = Field(None, title='허가일')
    construction_date: Optional[datetime] = Field(None, title='착공일')
    approval_date: Optional[datetime] = Field(None, title='사용승인일')
