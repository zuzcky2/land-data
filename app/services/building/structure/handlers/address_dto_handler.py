from typing import Dict, Any, List, Optional, Tuple
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
from app.services.building.structure.dtos.address_dto import AddressDto, BlockAddressDto
from app.services.location.boundary.dto import BoundaryItemDto


class AddressDtoHandler:

    def handle(self,
               address_raw: Dict[str, Any],
               processed_blocks_data: List[Dict],
               continuous_items: List[Dict],
               state_boundary: BoundaryItemDto,
               district_boundary: BoundaryItemDto) -> AddressDto:

        road_address_node = address_raw.get('road_address', {})
        bd_mgt_sn = road_address_node.get('road_address_id')

        # 1. 지오메트리 처리
        merged_geometry, center_pt = self._process_geometries(continuous_items)

        # 2. 지번 리스트 처리 (Main vs Related)
        main_block = None
        related_blocks = []

        for p_data in processed_blocks_data:
            block_dto = self._build_single_block_dto(
                raw=p_data['raw'],
                state_boundary=state_boundary,
                district_boundary=district_boundary,
                township_boundary=p_data['township'],
                village_boundary=p_data['village']
            )

            if p_data['raw'].get('representative_yn') == '1':
                main_block = block_dto
            related_blocks.append(block_dto)

        # 3. 도로명 정보 가공
        road_suffix = self._combine_num(road_address_node.get('build_mnnm'), road_address_node.get('build_slno'))
        road_nm = address_raw.get('road_nm', '')
        display_road = f"{road_nm} {road_suffix}".strip()

        # 도로명 주소 문자열 조합 (시도 시군구 도로명...)
        full_road_addr = f"{district_boundary.item_full_name} {display_road}"

        building_group = address_raw.get('road_address', {}).get('building_group', {})

        sgg_build_nm = building_group.get('sgg_build_nm').strip() if building_group.get('sgg_build_nm') else None
        build_nm = building_group.get('build_nm').strip() if building_group.get('build_nm') else None

        return AddressDto(
            address_id=f"{address_raw.get('road_code_id')}_{bd_mgt_sn}",
            building_manage_number=bd_mgt_sn,
            road_code_id=address_raw.get('road_code_id'),
            address_name=sgg_build_nm or build_nm or display_road,
            display_address_name=address_raw.get('road_nm'),
            state=state_boundary.item_code,
            state_name=state_boundary.item_name,
            state_short_name=state_boundary.short_name,
            district=district_boundary.item_code,
            district_name=district_boundary.item_name,
            township_admin=building_group.get('h_dong_code'),
            township_admin_name=building_group.get('h_dong_nm'),
            zip_code=building_group.get('zip_code'),
            is_apartment=building_group.get('is_apartment') == '1',
            main_block=main_block,
            related_blocks=related_blocks,
            road_name_code=address_raw.get('road_code'),
            road_name=road_nm,
            road_main=str(road_address_node.get('build_mnnm', '')),
            road_sub=str(road_address_node.get('build_slno', '')) if road_address_node.get('build_slno', '') else None,
            display_road=display_road,
            display_road_address=full_road_addr,
            display_road_short_address=full_road_addr.replace(state_boundary.item_name, state_boundary.short_name),
            display_road_include_address=f"{full_road_addr} ({main_block.township_name if main_block else ''})",
            display_road_include_short_address=f"{full_road_addr.replace(state_boundary.item_name, state_boundary.short_name)} ({main_block.township_name if main_block else ''})",
            latitude=float(center_pt.y) if center_pt else None,
            longitude=float(center_pt.x) if center_pt else None,
            geo_point={"type": "Point", "coordinates": [center_pt.x, center_pt.y]} if center_pt else None,
            geometry=merged_geometry
        )

    def _build_single_block_dto(self, raw, state_boundary, district_boundary, township_boundary,
                                village_boundary) -> BlockAddressDto:
        bmain = str(raw.get('lnbr_mnnm', ''))
        bsub = str(raw.get('lnbr_slno', ''))
        block_suffix = self._combine_num(bmain, bsub)

        # PNU 생성 (법정동10 + 산1 + 본번4 + 부번4)
        pnu = raw.get('bjd_code', '') + (raw.get('mountain_yn') or '0') + bmain.zfill(4) + bsub.zfill(4)

        # 전체 행정구역 주소 (시도 시군구 읍면동 리)
        boundary_parts = [district_boundary.item_full_name, township_boundary.item_name if township_boundary else ""]
        if village_boundary: boundary_parts.append(village_boundary.item_name)
        full_boundary = " ".join([p for p in boundary_parts if p]).strip()

        return BlockAddressDto(
            pnu=pnu,
            township=township_boundary.item_code if township_boundary else None,
            township_name=township_boundary.item_name if township_boundary else None,
            village=village_boundary.item_code if village_boundary else None,
            village_name=village_boundary.item_name if village_boundary else None,
            display_boundary_address=full_boundary,
            display_boundary_short_address=full_boundary.replace(state_boundary.item_name, state_boundary.short_name),
            is_mountain=raw.get('mountain_yn') == '1',
            is_representative=raw.get('representative_yn') == '1',
            sort_number=int(raw.get('serial_no')),
            block_main=bmain,
            block_sub=None if bsub == '0' else bsub,
            display_block=f"{township_boundary.item_name if township_boundary else ''} {block_suffix}".strip(),
            display_block_address=f"{full_boundary} {block_suffix}".strip(),
            display_block_short_address=f"{full_boundary.replace(state_boundary.item_name, state_boundary.short_name)} {block_suffix}".strip(),
        )

    def _process_geometries(self, items: List[Dict]) -> Tuple[Optional[Dict], Optional[Point]]:
        if not items: return None, None
        valid_shapes = []
        for item in items:
            geom = item.get('geometry')
            if not geom: continue
            try:
                s = shape(geom)
                if not s.is_valid: s = s.buffer(0)
                valid_shapes.append(s)
            except:
                continue
        if not valid_shapes: return None, None
        merged = unary_union(valid_shapes)
        return mapping(merged), merged.centroid

    def _combine_num(self, main: Any, sub: Any) -> str:
        m = str(main or '').strip()
        s = str(sub or '').strip()
        if not m: return ""
        return m if not s or s in ['0', '0000'] else f"{m}-{s}"