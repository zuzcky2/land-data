from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.service import BoundaryService
from app.services.location.raw.services.address_service import AddressService as RawAddressService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService
from app.services.building.structure.handlers.address_dto_handler import AddressDtoHandler
from app.services.building.structure.dtos.address_dto import AddressDto
from typing import Optional, Dict, Any, List
from app.core.helpers.log import Log
from datetime import datetime, timedelta
import time


class AddressService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self,
                 manager: AddressManager,
                 address_dto_handler: AddressDtoHandler,
                 boundary_service: BoundaryService,
                 raw_address_service: RawAddressService,
                 raw_point_geometry_service: PointGeometryService,
                 raw_continuous_geometry_service: ContinuousGeometryService,
                 ):
        self._manager = manager
        self.address_dto_handler = address_dto_handler
        self._boundary_service = boundary_service
        self._raw_address_service = raw_address_service
        self._raw_point_geometry_service = raw_point_geometry_service
        self._raw_continuous_geometry_service = raw_continuous_geometry_service

        # 🚀 메모리 캐시 저장소 초기화
        self._boundary_cache: Dict[str, BoundaryItemDto] = {}

    @property
    def logger_name(self) -> str:
        return 'building_structure_address'

    @property
    def manager(self) -> AddressManager:
        return self._manager

    def build_by_bd_mgt_sn(self, bd_mgt_sn: str) -> Optional[AddressDto]:
        address_raw = self._raw_address_service.get_detail({'bdMgtSn': bd_mgt_sn})
        if not address_raw:
            Log.get_logger(self.logger_name).warning(f"Raw address not found for: {bd_mgt_sn}")
            return None

        return self.build_by_address_raw(address_raw)

    def build_by_address_raw(self, address_raw: Dict[str, Any]) -> Optional[AddressDto]:
        bd_mgt_sn = address_raw.get('bdMgtSn')
        if not bd_mgt_sn:
            return None

        return self._run_build_pipeline(address_raw, bd_mgt_sn)

    def _run_build_pipeline(self, address_raw: Dict[str, Any], bd_mgt_sn: str) -> Optional[AddressDto]:
        # 전체 시작 시간 측정
        start_all = time.time()

        now = datetime.now()
        role_date = now - timedelta(days=90)

        # 1. 기존 데이터 확인 구간
        t_start_read = time.time()
        address = self.manager.driver(self.DRIVER_MONGODB).set_arguments({
            'building_manage_number': bd_mgt_sn,
            'updated_at': {'$gt': role_date}
        }).read_one()
        t_end_read = time.time()

        if address:
            return AddressDto(**address)

        try:
            # 2. 행정구역 정보 확보 구간
            t_start_boundary = time.time()
            state_boundary = self._get_cache_boundary(bd_mgt_sn[:2], 'state')
            district_boundary = self._get_cache_boundary(bd_mgt_sn[:5], 'district')

            if not district_boundary:
                fallback_sigungu = address_raw.get('admCd', '')[:5]
                legal_code = fallback_sigungu + bd_mgt_sn[5:]
                district_boundary = self._get_cache_boundary(legal_code[:5], 'district')
                township_boundary = self._get_cache_boundary(legal_code[:8], 'township')
                village_boundary = self._get_cache_boundary(legal_code[:10], 'village')
            else:
                township_boundary = self._get_cache_boundary(bd_mgt_sn[:8], 'township')
                village_boundary = self._get_cache_boundary(bd_mgt_sn[:10], 'village')
            t_end_boundary = time.time()

            if not state_boundary or not district_boundary or not township_boundary:
                return None

            # 3. 좌표(Point) 수집 구간 (외부 API 호출 예상)
            t_start_point = time.time()
            road_query = f"{address_raw.get('rn', '')} {address_raw.get('buldMnnm', '')}"
            if address_raw.get('buldSlno') and str(address_raw['buldSlno']).strip() not in ['', '0']:
                road_query += f"-{address_raw['buldSlno']}"

            point_pagination = self._raw_point_geometry_service.get_list_by_chain({
                'pnu': bd_mgt_sn[:19],
                'bd_mgt_sn': bd_mgt_sn,
                'updated_at': {'$gt': role_date},
                'query': road_query,
                'road_full_address': address_raw.get('roadAddr'),
                'parcel_address': f"{address_raw.get('emdNm')} {address_raw.get('lnbrMnnm')}-{address_raw.get('lnbrSlno')}",
                'bbox': district_boundary.bbox,
                'page': 1,
                'per_page': 100
            })
            t_end_point = time.time()

            # 4. 지적도(Continuous) 수집 루프 구간 (가장 유력한 병목 지점)
            t_start_loop = time.time()
            point_items = getattr(point_pagination, 'items', [])
            continuous_items = []
            for point_item in point_items:
                pt = point_item.get('point', {})
                if not pt.get('x') or not pt.get('y'): continue

                continuous = self._raw_continuous_geometry_service.get_detail_by_chain({
                    'id': point_item.get('continuous_id'),
                    'bdMgtSn': bd_mgt_sn,
                    'updated_at': {'$gt': role_date},
                    'latitude': float(pt['x']),
                    'longitude': float(pt['y'])
                })
                if continuous and 'id' in continuous:
                    continuous_items.append(continuous)
            t_end_loop = time.time()

            # 5. 핸들러 및 최종 저장 구간
            t_start_final = time.time()
            dto = self.address_dto_handler.handle(
                address_raw=address_raw,
                continuous_items=continuous_items,
                state_boundary=state_boundary,
                district_boundary=district_boundary,
                township_boundary=township_boundary,
                village_boundary=village_boundary
            )

            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])
            t_end_final = time.time()

            # ⏱️ 성능 리포트 출력
            total_elapsed = time.time() - start_all
            # 0.5초 이상 걸리는 경우에만 상세 로그 남김 (조절 가능)
            if total_elapsed > 0.5:
                Log.get_logger(self.logger_name).info(
                    f"⏱️ Slow Build [{bd_mgt_sn}] - {total_elapsed:.3f}s\n"
                    f"   1. DB Read: {t_end_read - t_start_read:.3f}s\n"
                    f"   2. Boundary: {t_end_boundary - t_start_boundary:.3f}s\n"
                    f"   3. Point API: {t_end_point - t_start_point:.3f}s\n"
                    f"   4. Cont. Loop: {t_end_loop - t_start_loop:.3f}s (Items: {len(point_items)})\n"
                    f"   5. Handle & Store: {t_end_final - t_start_final:.3f}s"
                )

            return dto

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"Build Pipeline Error [{bd_mgt_sn}]: {str(e)}")
            return None

    # --- 💡 캐싱 헬퍼 메서드 ---

    def _get_cache_boundary(self, item_code: str, location_type: str) -> Optional[BoundaryItemDto]:
        """시군구 단위 BBOX 캐싱"""
        if item_code not in self._boundary_cache:
            boundary = self._boundary_service.get_boundary({
                'item_code': item_code,
                'location_type': location_type,
                'use_polygon': False
            })
            # 결과가 없더라도 반복 조회를 방지하기 위해 None 저장
            self._boundary_cache[item_code] = boundary

            # 캐시가 너무 커지는 것을 방지 (간단한 클린업 로직 필요 시 추가)
            if len(self._boundary_cache) > 6000:
                self._boundary_cache.clear()

        return self._boundary_cache[item_code]


    def clear_internal_cache(self):
        """메모리 캐시 강제 초기화 (필요 시 호출)"""
        self._boundary_cache.clear()