from pydantic import Field
from typing import Optional
from app.services.contracts.dto import MongoModel


class UnitDto(MongoModel):
    register_manage_number: str = Field(title='전유부 mgmBldrgstPk — PK')
    parent_register_manage_number: str = Field(title='표제부 mgmBldrgstPk → buildings 참조 (mgmUpBldrgstPk)')
    building_manage_number: str = Field(title='bdMgtSn → complexes 참조')

    unit_name: Optional[str] = Field(None, title='호실명 (건물명 등)')
    main_purpose: Optional[str] = Field(None, title='주용도')
    sub_purpose: Optional[str] = Field(None, title='기타용도')
    is_collective: bool = Field(True, title='집합건물 여부 (True=집합, False=일반)')
