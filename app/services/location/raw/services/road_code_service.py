from app.services.contracts.dto import PaginationDto
from app.services.location.raw.managers.road_address_manager import RoadAddressManager
from app.services.location.raw.services.abstract_address_service import AbstractAddressService

class RoadCodeService(AbstractAddressService):
    def __init__(self, manager: RoadAddressManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_road_code'

    @property
    def manager(self) -> RoadAddressManager:
        return self._manager

    def get_road_code_aggregate(self, page: int = 1, per_page: int = 1000) -> PaginationDto:
        # 페이지네이션을 위한 skip 계산
        driver = self.manager.mongodb_driver

        total = driver._get_total_count()

        skip_count = (page - 1) * per_page

        pipeline = [
            # 2. 페이지네이션을 위한 정렬 및 제한 단계 추가
            # 💡 정렬은 페이지네이션 결과의 일관성을 위해 반드시 필요함
            {
                '$sort': {
                    'road_code': 1  # 또는 원하는 정렬 기준
                }
            },
            {
                '$skip': skip_count
            },
            {
                '$limit': per_page
            },
            # 1. 조인 및 데이터 결합 로직 유지
            {
                '$lookup': {
                    'from': 'location_raw_road_address',
                    'localField': 'road_code',
                    'foreignField': 'road_code',
                    'as': 'road_address'
                }
            },
            {
                '$unwind': '$road_address'
            },
            {
                '$lookup': {
                    'from': 'location_raw_building_group',
                    'localField': 'road_address.road_address_id',
                    'foreignField': 'road_address_id',
                    'as': 'road_address.building_group'
                }
            },
            {
                '$unwind': '$road_address.building_group'
            },
            {
                '$lookup': {
                    'from': 'location_raw_block_address',
                    'localField': 'road_address.road_address_id',
                    'foreignField': 'road_address_id',
                    'as': 'road_address.block_addresses'
                }
            }
        ]

        return driver.build_pagination(list(driver.collection.aggregate(pipeline)), total)