from typing import Dict, Any, Optional
from app.services.location.raw.managers.continuous_geometry_manager import ContinuousGeometryManager
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.services.abstract_service import AbstractService
from app.core.helpers.log import Log


class ContinuousGeometryService(AbstractService):

    def __init__(self, manager: ContinuousGeometryManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_continuous_geometry'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

    def get_detail_by_chain(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        item = None
        target_id = params.get('id')

        # 1. 기존 데이터 조회 (ID가 있을 경우)
        # updated_at 필터를 쿼리에 포함하여 is_expired 호출 생략
        if target_id:
            item = mongodb_driver.clear().set_arguments({
                'id': target_id,
                'updated_at': params.get('updated_at'),  # 90일 조건 포함
            }).read_one()

        # 2. 데이터가 없으면 VWorld 수집
        if not item:
            # 💡 [성능 팁] 여기서 잠깐!
            # 만약 좌표(lat, lon)로 이미 저장된 데이터가 있는지 먼저 확인하면 API 호출을 더 줄일 수 있습니다.

            vworld_driver = self.manager.driver(self.DRIVER_VWORLD)
            item = vworld_driver.clear().set_arguments({
                'latitude': params.get('latitude'),
                'longitude': params.get('longitude'),
            }).read_one()

            if item:
                item['bdMgtSn'] = params.get('bdMgtSn')
                # 🚀 store 시 manage_id 등을 활용해 중복 Insert 방지 확인 필요
                mongodb_driver.store([item])

        return item

    def sync_from_vworld(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        """외부 호출용 동기화 엔드포인트"""
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            item = self.get_detail_by_chain(params)
            if item:
                return {'status': 'success', 'bdMgtSn': item.get('bdMgtSn'), 'id': item.get('id')}

            return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {params}")
            raise e