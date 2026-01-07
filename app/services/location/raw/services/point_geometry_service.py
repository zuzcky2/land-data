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
        """DB 목록 조회 -> 만료 검사 -> VWorld 주소 검색 -> PNU 매칭 -> 저장"""
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        bd_mgt_sn = params.get('bdMgtSn')

        # 1. 로컬 DB 조회
        pagination = mongodb_driver.clear().set_pagination(
            params['page'], params['per_page']).set_arguments({'bdMgtSn': bd_mgt_sn}).read()

        # 2. 만료 체크 (첫 번째 아이템 기준 90일)
        is_data_exists = getattr(pagination, 'items', [])
        if is_data_exists and self.is_expired(pagination.items[0].get('_id'), 90):
            pagination.items = []

        # 3. 데이터가 없을 경우 VWorld 주소 검색(Geocoding) 수행
        if not pagination.items:
            vworld_driver = self.manager.driver(self.DRIVER_VWORLD)

            # BBOX와 쿼리로 좌표 검색
            vworld_pagination = vworld_driver.clear().set_arguments({
                'query': params.get('query'),
                'bbox': params.get('bbox')
            }).read()

            valid_items = []
            target_pnu = params.get('pnu')

            for item in getattr(vworld_pagination, 'items', []):
                # 검색 결과 중 요청한 PNU와 일치하는 데이터만 선별
                if item.get('id') == target_pnu:
                    point = item.get('point', {})
                    x, y = point.get('x'), point.get('y')

                    # 중복 방지를 위한 고유 관리 ID 생성 (건물번호+좌표)
                    item['bdMgtSn'] = bd_mgt_sn
                    item['manage_id'] = f"{bd_mgt_sn}_{x}_{y}"
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