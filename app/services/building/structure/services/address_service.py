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
        self._boundary_cache: Dict[str, BoundaryItemDto] = {}

    @property
    def logger_name(self) -> str:
        return 'building_structure_address'

    @property
    def manager(self) -> AddressManager:
        return self._manager

    def build_by_address_raw(self, address_raw: Dict[str, Any]) -> Optional[AddressDto]:
        now = datetime.now()
        role_date = now - timedelta(days=7)

        road_address_node = address_raw.get('road_address', {})
        road_address_id = road_address_node.get('road_address_id')

        if not road_address_id:
            return None

        address_exist = self.manager.driver(self.DRIVER_MONGODB).set_arguments({
            'building_manage_number': road_address_id,
            'updated_at': {'$gt': role_date}
        }).read_one()

        if address_exist:
            return AddressDto(**address_exist)

        try:
            state_boundary = self._get_cache_boundary(road_address_id[:2], 'state')
            district_boundary = self._get_cache_boundary(road_address_id[:5], 'district')

            # 🚀 지번, PNU 리스트 생성
            raw_blocks = road_address_node.get('block_addresses', [])
            parcel_addresses = []
            pnu_list = []
            processed_blocks_data = []

            for rb in raw_blocks:
                bjd = rb.get('bjd_code', '')
                bmain = str(rb.get('lnbr_mnnm', ''))
                bsub = str(rb.get('lnbr_slno', ''))

                # PNU 생성 및 리스트 추가
                pnu = bjd + (rb.get('mountain_yn') or '0') + bmain.zfill(4) + bsub.zfill(4)
                pnu_list.append(pnu)

                # 검색용 지번 주소 생성
                block_suffix = self._combine_num(bmain, bsub)
                full_parcel = f"{district_boundary.item_full_name if district_boundary else ''} {rb.get('emd_nm', '')} {block_suffix}".strip()
                parcel_addresses.append(full_parcel)

                processed_blocks_data.append({
                    'raw': rb,
                    'township': self._get_cache_boundary(bjd[:8], 'township'),
                    'village': self._get_cache_boundary(bjd, 'village') if len(bjd) >= 10 else None
                })

            road_suffix = self._combine_num(road_address_node.get('build_mnnm'), road_address_node.get('build_slno'))
            road_query = f"{address_raw.get('road_nm', '')} {road_suffix}".strip()
            road_full_address = f"{district_boundary.item_full_name if district_boundary else ''} {road_query}"

            # 🚀 pnu_list 추가 전달
            point_pagination = self._raw_point_geometry_service.get_list_by_chain({
                'bd_mgt_sn': road_address_id,
                'road_full_address': road_full_address,
                'parcel_addresses': parcel_addresses,
                'pnu_list': pnu_list,
                'query': road_query,
                'bbox': district_boundary.bbox,
                'page': 1,
                'per_page': 10
            })

            # 🛡️ point_pagination이 None일 경우를 대비한 방어 로직
            if not point_pagination:
                Log.get_logger(self.logger_name).warning(f"Point pagination returned None for [{road_address_id}]")
                # 필요시 여기서 빈 DTO를 만들거나 return None 처리
                point_items = []
            else:
                point_items = getattr(point_pagination, 'items', [])

            continuous_items = []
            for pt_item in point_items:
                pt = pt_item.get('point', {})
                # 좌표가 없는 경우 건너뜀
                if not pt.get('x') or not pt.get('y'):
                    continue

                continuous = self._raw_continuous_geometry_service.get_detail_by_chain({
                    'id': pt_item.get('continuous_id'),
                    'bdMgtSn': road_address_id,
                    'latitude': float(pt.get('x', 0)),
                    'longitude': float(pt.get('y', 0))
                })
                if continuous and 'id' in continuous:
                    continuous_items.append(continuous)

            dto = self.address_dto_handler.handle(
                address_raw=address_raw,
                processed_blocks_data=processed_blocks_data,
                continuous_items=continuous_items,
                state_boundary=state_boundary,
                district_boundary=district_boundary
            )

            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])

            return dto

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"Build Error [{road_address_id}]: {str(e)}", exc_info=True)
            return None

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