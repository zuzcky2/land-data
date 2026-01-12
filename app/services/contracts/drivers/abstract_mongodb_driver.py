from abc import abstractmethod, ABC
from app.services.contracts.drivers.abstract import AbstractDriver
from typing import Any, List, Optional, Tuple, Union
from pymongo import UpdateOne, ASCENDING, DESCENDING
from pymongo.collection import Collection
from datetime import datetime


class AbstractMongodbDriver(AbstractDriver, ABC):

    @property
    @abstractmethod
    def primary_key(self) -> str:
        pass

    @property
    @abstractmethod
    def collection(self) -> Collection:
        pass

    @property
    @abstractmethod
    def convert_types(self) -> dict:
        return {}

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        # 1. 필터 조건 복사 (원본 args 보존)
        filters = (self.args or {}).copy()

        # 2. 메타 파라미터(sort, page, per_page) 추출 및 필터에서 제거
        # self.page와 self.per_page는 이미 부모 클래스나 필드에 존재하므로 필터에서만 제거합니다.
        sort_params = filters.pop('sort', None)
        filters.pop('page', None)
        filters.pop('per_page', None)

        if single:
            doc = self.collection.find_one(filters)
            return [doc] if doc else []

        # 3. 쿼리 생성
        cursor = self.collection.find(filters)

        # 4. 정렬 처리
        if sort_params:
            formatted_sort = self._format_sort(sort_params)
            if formatted_sort:
                cursor = cursor.sort(formatted_sort)

        # 5. 페이징 처리
        skip = (self.page - 1) * self.per_page
        cursor = cursor.skip(skip).limit(self.per_page)

        return list(cursor)

    def _format_sort(self, sort_params: Any) -> Optional[List[Tuple[str, int]]]:
        if not sort_params:
            return None

        formatted = []
        if isinstance(sort_params, list):
            for item in sort_params:
                if isinstance(item, tuple) or isinstance(item, list):
                    key, direction = item
                    dir_val = ASCENDING if str(direction).lower() in ['1', 'asc'] else DESCENDING
                    formatted.append((key, dir_val))
        elif isinstance(sort_params, dict):
            for key, direction in sort_params.items():
                dir_val = ASCENDING if str(direction).lower() in ['1', 'asc'] else DESCENDING
                formatted.append((key, dir_val))

        return formatted if formatted else None

    def _get_total_count(self) -> int:
        # 카운트 시에도 필터 조건만 남기고 메타 정보는 제거
        filters = (self.args or {}).copy()
        filters.pop('sort', None)
        filters.pop('page', None)
        filters.pop('per_page', None)
        return self.collection.count_documents(filters)

    def store(self, items: List[dict]) -> Any:
        if not items:
            return None

        now = datetime.now()
        operations = []

        for item in items:
            # 1. 타입 변환 처리
            for key, set_type in self.convert_types.items():
                if key in item and item[key] is not None:
                    item[key] = set_type(item[key])

            # 2. PK 체크
            pk = item.get(self.primary_key)
            if not pk:
                continue

            # 3. 🚀 핵심: 전처리
            # 들어온 데이터에 혹시 created_at이 있다면 제거합니다.
            # (이유: 업데이트 시 기존 DB에 있는 진짜 생성 날짜를 지키기 위해)
            update_data = item.copy()
            update_data.pop('created_at', None)

            # updated_at은 언제나 현재 시간
            update_data['updated_at'] = now

            # Upsert를 위한 쿼리와 업데이트 내용 분리
            filter_query = {self.primary_key: pk}

            operations.append(UpdateOne(
                filter_query,
                {
                    '$set': update_data,  # 매번 업데이트
                    '$setOnInsert': {  # 문서가 처음 생성(Insert)될 때만 적용
                        'created_at': now
                    }
                },
                upsert=True
            ))

        if operations:
            return self.collection.bulk_write(operations)

        return None