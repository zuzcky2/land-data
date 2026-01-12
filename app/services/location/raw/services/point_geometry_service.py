from typing import Dict, Any, List
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.services.abstract_service import AbstractService
from app.core.helpers.log import Log


class PointGeometryService(AbstractService):

    def __init__(self, manager: Any):  # Manager 타입은 주입에 따라 유동적
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_point_geometry'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

    def get_list_by_chain(self, params: Dict[str, Any]) -> Any:
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        bd_mgt_sn = params.get('bd_mgt_sn')

        # 1. 로컬 DB 조회 (updated_at 인덱스 활용으로 이미 90일 필터링됨)
        pagination = mongodb_driver.clear().set_pagination(
            params['page'], params['per_page']).set_arguments({
            'bdMgtSn': bd_mgt_sn,
            'updated_at': params.get('updated_at')
        }).read()

        items = getattr(pagination, 'items', [])

        # 2. 데이터가 없거나 만료된 경우만 VWorld 호출
        # (is_expired 호출을 제거하고 쿼리 결과가 없으면 바로 VWorld 실행)
        if not items:
            vworld_driver = self.manager.driver(self.DRIVER_VWORLD)

            # API 호출 (이 구간이 1.2초 소요됨)
            vworld_pagination = vworld_driver.clear().set_arguments({
                'query': params.get('query'),
                'bbox': params.get('bbox')
            }).read()

            valid_items = []
            target_pnu = params.get('pnu')
            target_road = params.get('road_full_address')
            target_parcel = params.get('parcel_address')

            for item in getattr(vworld_pagination, 'items', []):
                addr = item.get('address', {})
                # 매칭 조건 최적화
                is_match = (
                        item.get('id') == target_pnu or
                        addr.get('road') == target_road or
                        addr.get('parcel') == target_parcel
                )

                if is_match:
                    pt = item.get('point', {})
                    x, y = pt.get('x'), pt.get('y')

                    # 데이터 구조 정리
                    item.update({
                        'bdMgtSn': bd_mgt_sn,
                        'manage_id': f"{bd_mgt_sn}_{x}_{y}"
                    })
                    valid_items.append(item)

            if valid_items:
                mongodb_driver.store(valid_items)
                pagination.items = valid_items

        return pagination

    def sync_from_vworld(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        """외부 호출용 동기화 엔드포인트"""
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            # Point 데이터는 목록을 반환하므로 list_by_chain 호출
            pagination = self.get_list_by_chain(params)

            if pagination.items:
                return {'status': 'success', 'count': len(pagination.items)}

            return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {params}")
            raise e