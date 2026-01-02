from abc import abstractmethod, ABC

from app.services.contracts.drivers.abstract import AbstractDriver
from typing import Any, List
from pymongo import UpdateOne
from pymongo.collection import Collection


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
        filters = self.args or {}
        if single:
            doc = self.collection.find_one(filters)
            return [doc] if doc else []

        skip = (self.page - 1) * self.per_page
        cursor = self.collection.find(filters).skip(skip).limit(self.per_page)
        return list(cursor)

    def _get_total_count(self) -> int:
        return self.collection.count_documents(self.args or {})

    def store(self, items: List[dict]) -> Any:
        if not items:
            return None

        operations = []
        for item in items:

            for key, set_type in self.convert_types.items():
                if key in item and item[key] is not None:
                    item[key] = set_type(item[key])

            # 1. 고유 키 추출
            pk = item.get(self.primary_key)

            if not pk:
                continue

            operations.append(UpdateOne(
                {self.primary_key: pk},  # 조회 키도 문자열로
                {'$set': item},
                upsert=True
            ))

        if operations:
            return self.collection.bulk_write(operations)

        return None