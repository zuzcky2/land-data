from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.service import BoundaryService
from app.services.location.raw.services.address_service import AddressService as RawAddressService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService
from app.services.building.structure.handlers.address_make_dto_handler import AddressDtoHandler
from app.services.building.structure.dtos.address_dto import AddressDto
from typing import Optional, Dict, Any, List
from app.core.helpers.log import Log


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
        try:
            # 1. 행정구역 정보 및 BBOX 확보
            state_boundary = self._get_cache_boundary(bd_mgt_sn[:2], 'state')
            district_boundary = self._get_cache_boundary(bd_mgt_sn[:5], 'district')
            township_boundary = self._get_cache_boundary(bd_mgt_sn[:8], 'township')
            village_boundary = self._get_cache_boundary(bd_mgt_sn[:10], 'village')

            bbox = district_boundary.bbox if district_boundary else None

            # 2. 도로명 주소 쿼리 생성
            road_query = f"{address_raw.get('rn', '')} {address_raw.get('buldMnnm', '')}"
            if address_raw.get('buldSlno') and str(address_raw['buldSlno']).strip() not in ['', '0']:
                road_query += f"-{address_raw['buldSlno']}"

            # 3. 좌표(Point) 수집
            point_pagination = self._raw_point_geometry_service.get_list_by_chain({
                'pnu': bd_mgt_sn[:19],
                'bd_mgt_sn': bd_mgt_sn,
                'query': road_query,
                'bbox': bbox,
                'page': 1,
                'per_page': 1000
            })

            # 4. 지적도(Continuous) 수집 및 포인트 보정 (중요 로직 반영)
            poly_data = None
            point_items = getattr(point_pagination, 'items', [])

            continuous_items = []
            for point_item in point_items:
                point = point_item.get('point', {})
                if not point.get('x') or not point.get('y'):
                    continue

                # 지적도 상세 정보 수집 (Chain)
                continuous = self._raw_continuous_geometry_service.get_detail_by_chain({
                    'id': point_item.get('continuous_id'),
                    'bdMgtSn': bd_mgt_sn,
                    'latitude': float(point['x']),
                    'longitude': float(point['y'])
                })

                if continuous and 'id' in continuous:
                    continuous_items.append(continuous)

                    # 포인트 보정 로직
                    if not point_item.get('continuous_id'):
                        point_item['continuous_id'] = continuous['id']
                        self._raw_point_geometry_service.manager.driver('mongodb').store([point_item])

            # 5. 핸들러를 통한 DTO 생성 및 매핑
            dto = self.address_dto_handler.handle(
                address_raw=address_raw,
                continuous_items=continuous_items,  # 수집된 리스트 그대로 전달
                state_boundary=state_boundary,
                district_boundary=district_boundary,
                township_boundary=township_boundary,
                village_boundary=village_boundary
            )

            # 6. 최종 addresses 컬렉션 저장
            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])

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