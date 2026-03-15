from pydantic import Field
from typing import Optional
from app.services.contracts.dto import MongoModel


class FloorDto(MongoModel):
    floor_id: str = Field(title='층 고유 ID — PK ({register_manage_number}_{flrGbCd}_{flrNo})')
    register_manage_number: str = Field(title='표제부 mgmBldrgstPk → buildings 참조')
    building_manage_number: str = Field(title='bdMgtSn → complexes 참조')

    floor_type: str = Field(title='지상/지하 구분 (지상, 지하)')
    floor_type_code: str = Field(title='flrGbCd (10=지하, 20=지상)')
    floor_number: int = Field(title='층번호 (flrNo)')
    floor_name: str = Field(title='층명칭 (예: 1층, 지2)')

    area: float = Field(0.0, title='해당 층 면적 (㎡)')
    main_purpose: Optional[str] = Field(None, title='주용도')
    sub_purpose: Optional[str] = Field(None, title='기타용도')
    is_main_building: bool = Field(True, title='주건축물 여부')
