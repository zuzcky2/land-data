from typing import Dict, Any, List
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.services.abstract_service import AbstractService
from app.core.helpers.log import Log


class PointGeometryService(AbstractService):

    def __init__(self, manager: Any):
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

        pagination = mongodb_driver.clear().set_pagination(
            params['page'], params['per_page']).set_arguments({
            'bdMgtSn': bd_mgt_sn,
            'updated_at': params.get('updated_at')
        }).read()

        items = pagination.items

        if not items:
            vworld_driver = self.manager.driver(self.DRIVER_VWORLD)

            vworld_pagination = vworld_driver.clear().set_arguments({
                'query': params.get('query'),
                'bbox': params.get('bbox')
            }).read()

            valid_items = []
            # 🚀 pnu_list 배열 수신
            target_pnu_list = params.get('pnu_list') or []
            target_road = params.get('road_full_address') or ""
            target_parcels = params.get('parcel_addresses') or []

            for item in getattr(vworld_pagination, 'items', []):
                addr = item.get('address', {})
                v_id = item.get('id', '')
                v_road = addr.get('road', '')
                v_parcel = addr.get('parcel', '')

                # --- 🚀 매칭 조건 최적화 ---

                # A. PNU 리스트 중 하나라도 일치하는지 확인
                pnu_match = (v_id and v_id in target_pnu_list)

                # B. 도로명 주소 포함 여부 (VWorld 결과가 요청 주소를 포함하는지)
                road_match = (target_road and target_road in v_road)

                # C. 지번 주소 리스트 중 하나라도 일치하는지 확인
                parcel_match = (v_parcel and v_parcel in target_parcels)

                if pnu_match or road_match or parcel_match:
                    pt = item.get('point', {})
                    x, y = pt.get('x'), pt.get('y')

                    item.update({
                        'bdMgtSn': bd_mgt_sn,
                        'manage_id': f"{bd_mgt_sn}_{x}_{y}",
                        'updated_at': params.get('updated_at') or ""
                    })
                    valid_items.append(item)

            if valid_items:
                mongodb_driver.store(valid_items)
                pagination.items = valid_items

        return pagination

    def sync_from_vworld(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            pagination = self.get_list_by_chain(params)
            if pagination and getattr(pagination, 'items', []):
                return {'status': 'success', 'count': len(pagination.items)}

            return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {params}")
            raise e