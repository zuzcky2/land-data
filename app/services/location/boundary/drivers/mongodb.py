# app/services/location/boundary/drivers/mongodb.py

from typing import List, Optional, Any
from copy import deepcopy
from pymongo.collection import UpdateOne, Collection
from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.drivers.interface import BoundaryStoreResult, BoundaryInterface
from app.services.location.boundary.types.boundary import STATE
from app.facade import db


class MongoDBDriver(BoundaryInterface):
    client: Collection

    def __init__(self):
        # 인터페이스 초기화 (필요 시)
        super().__init__()
        driver_name = 'mongodb'
        database_name = 'landmark'
        collection_name = 'boundary'
        self.client = db.get_mongodb_driver(driver_name).get_database(database_name).get_collection(collection_name)

    def _build_read_process(self):
        args = self.args or {}
        filters = {}
        projection = {}
        sorts = args.get('sort', [])

        location_fields = [
            'location_type', 'jurisdiction_type', 'item_code', 'item_name',
            'state_code', 'district_code', 'township_code', 'village_code'
        ]
        for field in location_fields:
            if args.get(field):
                filters[field] = args[field]

        if args.get('use_polygon') == 0:
            projection['geo_polygon'] = 0

        self.count_filters = deepcopy(filters)

        if args.get('latitude') and args.get('longitude'):
            filters['geo_polygon'] = {
                '$near': {
                    '$geometry': {
                        'type': 'Point',
                        'coordinates': [float(args['longitude']), float(args['latitude'])],
                    }
                }
            }
            sorts = []

        self.filters = filters
        self.projection = projection
        self.sorts = sorts if len(sorts) > 0 else None

    def _fetch_raw(self, single: bool = False) -> List[BoundaryItemDto]:
        """MongoDB에서 데이터를 꺼내 BoundaryItemDto 객체 리스트로 직접 변환합니다."""
        self._build_read_process()

        if single:
            doc = self.client.find_one(self.filters, self.projection)
            return [BoundaryItemDto(**doc)] if doc else []

        skip = (self.page - 1) * self.per_page
        cursor = self.client.find(self.filters, self.projection)

        if self.sorts:
            cursor = cursor.sort(self.sorts)

        # DB에서 가져온 dict 데이터를 BoundaryItemDto로 즉시 변환
        return [BoundaryItemDto(**doc) for doc in cursor.skip(skip).limit(self.per_page)]

    def _get_total_count(self) -> int:
        if not hasattr(self, 'count_filters'):
            self._build_read_process()
        return self.client.count_documents(self.count_filters)

    def store(self, items: List[BoundaryItemDto]) -> BoundaryStoreResult:
        operations = []
        for item in items:
            if item.location_type == STATE:
                item.geo_polygon = None

            item_data = item.model_dump() if hasattr(item, 'model_dump') else item.dict()

            op = UpdateOne(
                {
                    'item_code': item.item_code,
                    'location_type': item.location_type,
                    'jurisdiction_type': item.jurisdiction_type
                },
                {'$set': item_data},
                upsert=True
            )
            operations.append(op)

        if not operations:
            return BoundaryStoreResult(success=True)

        result = self.client.bulk_write(operations)

        return BoundaryStoreResult(
            matched_count=result.matched_count,
            modified_count=result.modified_count,
            upserted_count=result.upserted_count,
            success=True,
            raw_response=result.bulk_api_result
        )

__all__ = ['MongoDBDriver']