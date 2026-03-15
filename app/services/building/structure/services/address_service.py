from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.service import BoundaryService
from app.services.location.raw.services.block_address_service import BlockAddressService
from app.services.location.raw.services.building_group_service import BuildingGroupService
from app.services.location.raw.services.road_address_service import RoadAddressService
from app.services.location.raw.services.road_code_service import RoadCodeService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService
from app.services.building.structure.handlers.address_dto_handler import AddressDtoHandler
from app.services.building.structure.dtos.address_dto import AddressDto
from typing import Optional, Dict, Any
from app.core.helpers.log import Log
from datetime import datetime, timedelta


class AddressService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self,
                 manager: AddressManager,
                 address_dto_handler: AddressDtoHandler,
                 boundary_service: BoundaryService,
                 raw_road_address_service: RoadAddressService,
                 raw_road_code_service: RoadCodeService,
                 raw_block_address_service: BlockAddressService,
                 raw_building_group_service: BuildingGroupService,
                 raw_point_geometry_service: PointGeometryService,
                 raw_continuous_geometry_service: ContinuousGeometryService,
                 ):
        self._manager = manager
        self.address_dto_handler = address_dto_handler
        self._boundary_service = boundary_service
        self._raw_road_address_service = raw_road_address_service
        self._raw_road_code_service = raw_road_code_service
        self._raw_block_address_service = raw_block_address_service
        self._raw_building_group_service = raw_building_group_service
        self._raw_point_geometry_service = raw_point_geometry_service
        self._raw_continuous_geometry_service = raw_continuous_geometry_service
        self._boundary_cache: Dict[str, BoundaryItemDto] = {}

    @property
    def logger_name(self) -> str:
        return 'building_structure_address'

    @property
    def manager(self) -> AddressManager:
        return self._manager

    def build_by_building_raw(self, building_raw: Dict[str, Any]) -> Optional[AddressDto]:
        """
        건물 raw 데이터(group_info 또는 title_info 일반건축물)를 기반으로
        addresses 컬렉션에 bdMgtSn 기준 1:1 주소를 생성/갱신합니다.
        """
        bd_mgt_sn = building_raw.get('bdMgtSn')
        if not bd_mgt_sn:
            return None

        now = datetime.now()
        role_date = now - timedelta(days=7)
        geo_cache_date = now - timedelta(days=180)  # geometry 캐시는 180일 유효

        # 최근 7일 이내 갱신된 데이터는 스킵
        existing = self.manager.driver(self.DRIVER_MONGODB).set_arguments({
            'building_manage_number': bd_mgt_sn,
            'updated_at': {'$gt': role_date}
        }).read_one()

        if existing:
            return AddressDto(**existing)

        try:
            sigungu_cd = str(building_raw.get('sigunguCd', '')).strip()
            na_road_cd = str(building_raw.get('naRoadCd', '')).strip()

            # 1. 행정구역 경계 조회
            state_boundary = self._get_cache_boundary(sigungu_cd[:2], 'state')
            district_boundary = self._get_cache_boundary(sigungu_cd, 'district')

            if not state_boundary or not district_boundary:
                Log.get_logger(self.logger_name).warning(f"Boundary not found for sigunguCd [{sigungu_cd}]")
                return None

            # 2. 도로명 주소 조회 (bdMgtSn = road_address_id)
            road_address = self._raw_road_address_service.get_detail({'road_address_id': bd_mgt_sn})
            if not road_address:
                Log.get_logger(self.logger_name).warning(f"Road address not found for bdMgtSn [{bd_mgt_sn}]")
                return None

            # 3. 도로명 코드 조회 (naRoadCd 기준, emd_sn!='00' 우선)
            road_code_item = self._get_road_code_by_na_road_cd(na_road_cd)

            # 4. 지번 주소 목록 조회
            block_addr_pagination = self._raw_block_address_service.get_list({
                'road_address_id': bd_mgt_sn,
                'per_page': 100
            })
            raw_blocks = getattr(block_addr_pagination, 'items', [])

            # 5. 건물 그룹 정보 조회 (행정동, 우편번호, 아파트 여부)
            building_group = self._raw_building_group_service.get_detail({'road_address_id': bd_mgt_sn})

            # 6. 지번 전처리 및 PNU 생성
            parcel_addresses = []
            pnu_list = []
            processed_blocks_data = []

            for rb in raw_blocks:
                bjd = rb.get('bjd_code', '')
                bmain = str(rb.get('lnbr_mnnm', ''))
                bsub = str(rb.get('lnbr_slno', ''))

                pnu = bjd + (rb.get('mountain_yn') or '0') + bmain.zfill(4) + bsub.zfill(4)
                pnu_list.append(pnu)

                block_suffix = self._combine_num(bmain, bsub)
                full_parcel = f"{district_boundary.item_full_name} {rb.get('emd_nm', '')} {block_suffix}".strip()
                parcel_addresses.append(full_parcel)

                processed_blocks_data.append({
                    'raw': rb,
                    'township': self._get_cache_boundary(bjd[:8], 'township'),
                    'village': self._get_cache_boundary(bjd, 'village') if len(bjd) >= 10 else None
                })

            # 7. 공간정보(geometry) 조회
            road_nm = road_code_item.get('road_nm', '') if road_code_item else ''
            road_suffix = self._combine_num(road_address.get('build_mnnm'), road_address.get('build_slno'))
            road_query = f"{road_nm} {road_suffix}".strip()
            road_full_address = f"{district_boundary.item_full_name} {road_query}"

            point_pagination = self._raw_point_geometry_service.get_list_by_chain({
                'bd_mgt_sn': bd_mgt_sn,
                'road_full_address': road_full_address,
                'parcel_addresses': parcel_addresses,
                'pnu_list': pnu_list,
                'query': road_query,
                'updated_at': {'$gt': geo_cache_date},
                'bbox': district_boundary.bbox,
                'page': 1,
                'per_page': 10
            })

            point_items = getattr(point_pagination, 'items', []) if point_pagination else []

            continuous_items = []
            for pt_item in point_items:
                pt = pt_item.get('point', {})
                if not pt.get('x') or not pt.get('y'):
                    continue

                continuous = self._raw_continuous_geometry_service.get_detail_by_chain({
                    'id': pt_item.get('continuous_id'),
                    'bdMgtSn': bd_mgt_sn,
                    'latitude': float(pt.get('x', 0)),
                    'longitude': float(pt.get('y', 0)),
                    'updated_at': {'$gt': geo_cache_date},
                })

                if continuous and 'id' in continuous:
                    continuous_items.append(continuous)
                    pt_item['continuous_id'] = continuous['id']
                    self._raw_point_geometry_service.manager.mongodb_driver.store([pt_item])

            # 8. DTO 생성 및 저장
            dto = self.address_dto_handler.handle(
                building_raw=building_raw,
                road_address=road_address,
                road_code=road_code_item,
                building_group=building_group,
                processed_blocks_data=processed_blocks_data,
                continuous_items=continuous_items,
                state_boundary=state_boundary,
                district_boundary=district_boundary
            )

            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])

            return dto

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"Build Error [{bd_mgt_sn}]: {str(e)}", exc_info=True)
            return None

    def _get_road_code_by_na_road_cd(self, na_road_cd: str) -> Optional[Dict]:
        """도로명코드로 road_code 레코드를 조회합니다. emd_sn!='00'(특정 법정동) 우선."""
        if not na_road_cd or na_road_cd == ' ':
            return None
        item = self._raw_road_code_service.get_detail({
            'road_code': na_road_cd,
            'emd_sn': {'$ne': '00'}
        })
        if item:
            return item
        return self._raw_road_code_service.get_detail({'road_code': na_road_cd})

    def _get_cache_boundary(self, item_code: str, location_type: str) -> Optional[BoundaryItemDto]:
        if not item_code: return None
        if item_code not in self._boundary_cache:
            self._boundary_cache[item_code] = self._boundary_service.get_boundary({
                'item_code': item_code,
                'location_type': location_type,
                'use_polygon': False
            })
        return self._boundary_cache[item_code]

    def _combine_num(self, main: Any, sub: Any) -> str:
        m = str(main or '').strip()
        s = str(sub or '').strip()
        if not m: return ""
        return m if not s or s in ['0', '0000'] else f"{m}-{s}"
