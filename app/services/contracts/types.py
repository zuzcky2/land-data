from typing import Union, List, Tuple, Dict, Generic, TypeVar
from pydantic import BaseModel, root_validator
from pydantic.generics import GenericModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    per_page: int
    total: int
    last_page: int

class Pagination(GenericModel, Generic[T]):
    meta: PaginationMeta
    items: List[T]

    @root_validator(pre=True)
    def auto_convert_items(cls, values: dict):
        items = values.get("items", [])
        if not isinstance(items, list) or not items:
            return values

        # items 필드의 타입 정보 가져오기
        items_field = cls.__fields__.get("items")
        if not items_field:
            return values

        # 필드 타입이 List[T] 형태인지 확인
        target_type = items_field.type_

        # 만약 target_type이 BoundaryItemDto 같은 클래스이고,
        # 이미 items의 첫 번째 요소가 그 클래스의 인스턴스라면 변환 생략
        if isinstance(items[0], target_type):
            return values

        # 변환 로직 (필요한 경우에만 실행)
        try:
            # target_type이 List[T]의 T를 직접 가리키는 경우 (Pagination[T] 바인딩 후)
            if hasattr(target_type, "__init__") and isinstance(items[0], dict):
                values["items"] = [target_type(**item) for item in items]
        except Exception:
            # 변환 실패 시 원본 유지 (드라이버에서 이미 처리했으므로 대개 여기까지 안 옴)
            pass

        return values

