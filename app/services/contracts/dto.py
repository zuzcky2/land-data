from pydantic import BaseModel, Field, validator
from typing import List, Any, TypeVar, Generic, Optional
from pydantic.generics import GenericModel # GenericModel 임포트
import math

T = TypeVar("T")


class PaginationDto(GenericModel, Generic[T]):
    """
    페이지네이션된 목록에 대한 데이터 전송 객체 (DTO)입니다.
    """
    page: int = Field(1, title='현재 페이지')
    per_page: int = Field(1, title='페이지별 아이템 수량')
    total: int = Field(1, title='총 아이템 수')
    items: List[T] = Field(default_factory=list, title='아이템 목록')

    # last_page를 property로 만들면 데이터가 바뀔 때마다 자동으로 계산됩니다.
    @property
    def last_page(self) -> int:
        if self.total <= 0:
            return 1
        return math.ceil(self.total / self.per_page)

class MongoModel(BaseModel):
    """
    MongoDB 데이터 호환 베이스 모델 (Pydantic v1 버전)
    """
    id: Optional[Any] = Field(None, alias='_id', title='객체 ID')

    class Config:
        # JSON key(id)와 alias(_id) 모두 사용하여 데이터 주입 허용
        allow_population_by_field_name = True
        # ObjectId와 같은 외부 타입 허용
        arbitrary_types_allowed = True

    @validator('id', pre=True, always=True)
    def transform_id(cls, v):
        """ObjectId 객체를 문자열로 변환"""
        if v is None:
            return None
        return str(v)