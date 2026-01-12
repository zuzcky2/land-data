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
        """DB 조회 -> 만료 검사 -> VWorld 수집 -> 저장 파이프라인"""
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        item = None

        # 1. 기존 데이터 조회 (ID가 있을 경우)
        target_id = params.get('id')

        if target_id:
            item = mongodb_driver.clear().set_arguments({
                'id': target_id,
                'updated_at': params.get('updated_at'),
            }).read_one()

        # 2. 데이터 유효성 검사 (만료 여부 확인: 90일)
        if item and self.is_expired(item.get('_id'), 90):
            item = None

        # 3. 데이터가 없거나 만료된 경우 VWorld에서 새로 수집
        if not item:
            vworld_driver = self.manager.driver(self.DRIVER_VWORLD)

            # VWorld API 호출 (좌표 기반 지적 정보 조회)
            item = vworld_driver.clear().set_arguments({
                'latitude': params.get('latitude'),
                'longitude': params.get('longitude'),
            }).read_one()

            if item:
                # 메타데이터 보강 및 저장
                item['bdMgtSn'] = params.get('bdMgtSn')
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