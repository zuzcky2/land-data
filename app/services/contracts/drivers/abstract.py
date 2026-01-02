from abc import ABC
from typing import Any, Dict, Optional, Type, Sequence, List

from app.services.contracts.types import Pagination, PaginationMeta


class AbstractDriver(ABC):
    """
    모든 데이터 페칭 드라이버의 베이스 클래스
    DTO 타입은 각 Driver가 item_type으로 지정
    기본값은 dict → ETL/Raw 파이프라인에 적합
    """

    # dict 기본값 → DTO 지정 안 한 드라이버는 dict 그대로 리턴
    item_type: Type[Any] = dict

    args: Optional[Dict[str, Any]] = None
    page: int = 1
    per_page: int = 1000
    use_pagination: bool = False

    def set_arguments(self, args: Optional[Dict[str, Any]] = None):
        self.args = args or {}
        return self

    def set_pagination(self, page: int = 1, per_page: int = 1000):
        self.page = page
        self.per_page = per_page
        self.use_pagination = True
        return self

    def arguments(self, key: str, default=None):
        return self.args.get(key, default) if self.args else default

    def clear(self):
        self.page = 1
        self.per_page = 1000
        self.use_pagination = False
        self.args = {}
        return self

    def build_pagination(self, items: Sequence[Any], total: int) -> Any:
        """
        주어진 데이터를 페이징 객체로 변환합니다.
        제네릭 타입 T를 self.item_type으로 바인딩하여 Pydantic 에러를 방지합니다.
        """
        parsed_items: List[Any] = []

        for row in items:
            # 1. DTO 변환 로직 (기존 로직 유지)
            if self.item_type is not dict and isinstance(row, dict):
                parsed_items.append(self.item_type(**row))
            else:
                parsed_items.append(row)

        # 2. 페이징 메타 정보 계산
        last_page = (total + self.per_page - 1) // self.per_page if total > 0 else 1

        # 3. 중요: Pagination 클래스에 실제 타입을 주입 (Binding)
        # self.item_type이 dict라면 Pagination[dict]가 되고,
        # BoundaryItemDto라면 Pagination[BoundaryItemDto]가 됩니다.
        bound_pagination_class = Pagination[self.item_type]

        return bound_pagination_class(
            meta=PaginationMeta(
                page=self.page,
                per_page=self.per_page,
                total=total,
                last_page=last_page,
            ),
            items=parsed_items,
        )