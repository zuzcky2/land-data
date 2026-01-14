from app.services.location.raw.managers.address_manager import AddressManager
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.services.abstract_service import AbstractService
from typing import Dict, Any, Optional
from app.core.helpers.log import Log


class AddressService(AbstractService):

    def __init__(self, manager: AddressManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_address'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

    def get_detail_by_chain(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        # 1. MongoDB에서 기존 주소 정보 조회
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        item = mongodb_driver.clear().set_arguments(params).read_one()

        # 2. 검색 쿼리로 사용된 주소(newPlatPlc) 목록 추출
        incoming_queries = params.get('search_queries', {}).get('$in', [])

        def store_search_queries(queries: list, origin: dict):
            change = False
            if 'search_queries' not in origin:
                origin['search_queries'] = []
                change = True

            for query in queries:
                query = query.strip()
                if query and query not in origin['search_queries']:
                    origin['search_queries'].append(query)
                    change = True

            if change:
                mongodb_driver.store([origin])

        # 3. DB에 데이터가 없는 경우 외부 API(JGK)에서 신규 조회
        if not item:
            jgk_driver = self.manager.driver(self.DRIVER_JGK)
            item = (jgk_driver.clear()
                .set_arguments({'search_queries': incoming_queries})
                .set_pagination(page=1, per_page=1)
                .read_one())

        # [핵심 수정] 검증 로직 추가
        if item:
            road_addr_part = item.get('roadAddrPart1')
            # 검색 조건(newPlatPlc) 중 하나라도 roadAddrPart1을 포함하고 있는지 확인
            # (문자열 포함 여부 체크: road_addr_part in query)
            is_valid = any(
                str(query).strip() and road_addr_part and road_addr_part in query 
                for query in incoming_queries
            )

            if not is_valid:
                # 포함되지 않는다면 잘못된 매칭으로 간주하고 중단
                Log.get_logger(self.logger_name).warning(
                    f"[INVALID_MATCH_BLOCKED] RoadAddr: {road_addr_part} not in Queries: {incoming_queries}"
                )
                return None

            # 검증 통과 시 검색 쿼리 업데이트 및 저장
            store_search_queries(incoming_queries, item)

        return item

    def sync_from_jgk(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            # get_detail_by_chain 내부에서 검증을 거쳐 적합하지 않으면 None 반환
            item = self.get_detail_by_chain({
                'search_queries': params.get('search_queries'),
                'updated_at': params.get('updated_at')
            })

            if item:
                return {'status': 'success', 'bdMgtSn': item.get('bdMgtSn')}
            else:
                # 검증 실패(None) 시 dead 처리를 통해 무한 재시도 방지
                return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {str(params)}")
            raise e