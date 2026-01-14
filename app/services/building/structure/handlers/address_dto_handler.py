from typing import Dict, Any, List, Optional, Tuple
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
from app.services.building.structure.dtos.address_dto import AddressDto
from app.services.location.boundary.dto import BoundaryItemDto


class AddressDtoHandler:

    def handle(self,
               address_raw: Dict[str, Any],
               continuous_items: List[Dict],
               state_boundary: BoundaryItemDto,
               district_boundary: BoundaryItemDto,
               township_boundary: BoundaryItemDto,
               village_boundary: Optional[BoundaryItemDto]) -> AddressDto:

        bd_mgt_sn = address_raw.get('bdMgtSn')

        # 1. 폴리곤 병합 및 중앙점 추출 (데이터 없으면 None 반환)
        merged_geometry, center_pt = self._process_geometries(continuous_items)

        # 2. 행정구역 명칭 및 짧은 명칭 설정
        full_state = state_boundary.item_name
        short_state = state_boundary.short_name
        display_boundary_address = village_boundary.item_full_name if village_boundary else township_boundary.item_full_name

        # 3. 관련 지번(Related Blocks) 가공
        processed_related_blocks = self._process_related_blocks(
            address_raw.get('relJibun', []),
            full_state,
            district_boundary.item_name,
            township_boundary.item_name
        )

        # 4. 도로명/지번 본부번 결합 (예: 123-0 -> 123)
        road_suffix = self._combine_num(address_raw.get('buldMnnm'), address_raw.get('buldSlno'))
        block_suffix = self._combine_num(address_raw.get('lnbrMnnm'), address_raw.get('lnbrSlno'))
        raw_bd_nm = address_raw.get('bdNm')
        address_name = raw_bd_nm.strip() if raw_bd_nm and raw_bd_nm.strip() else None


        # 5. DTO 생성 및 반환
        return AddressDto(
            building_manage_number=bd_mgt_sn,
            pnu=bd_mgt_sn[:19],
            address_name=address_name,
            display_address_name=address_name if address_name else address_raw.get('rn'),

            # 행정구역 매핑
            state=state_boundary.item_code,
            state_name=full_state,
            state_short_name=short_state,
            district=district_boundary.item_code,
            district_name=district_boundary.item_name,
            township=township_boundary.item_code,
            township_name=township_boundary.item_name,
            village=village_boundary.item_code if village_boundary else None,
            village_name=village_boundary.item_name if village_boundary else None,

            township_admin=address_raw.get('admCd'),
            township_admin_name=address_raw.get('hemdNm'),
            zip_code=address_raw.get('zipNo'),
            is_current=address_raw.get('hstryYn') == '0',

            display_boundary_address=display_boundary_address,
            display_boundary_short_address=display_boundary_address.replace(full_state, short_state),

            # --- 지번 주소 상세 ---
            is_mountain=address_raw.get('mtYn') == '1',
            block_main=self._to_int(address_raw.get('lnbrMnnm')),
            block_sub=self._to_int(address_raw.get('lnbrSlno')),
            display_block=f"{address_raw.get('emdNm', '')} {block_suffix}".strip(),
            display_block_address=address_raw.get('jibunAddr'),
            display_block_short_address=address_raw.get('jibunAddr', '').replace(full_state, short_state),
            related_blocks=processed_related_blocks,

            # --- 도로명 주소 상세 ---
            road_name_code=address_raw.get('rnMgtSn'),
            road_name=address_raw.get('rn'),
            road_main=self._to_int(address_raw.get('buldMnnm')),
            road_sub=self._to_int(address_raw.get('buldSlno')),
            display_road=f"{address_raw.get('rn', '')} {road_suffix}".strip(),
            display_road_address=address_raw.get('roadAddrPart1'),
            display_road_short_address=address_raw.get('roadAddrPart1', '').replace(full_state, short_state),
            display_road_include_address=address_raw.get('roadAddr'),
            display_road_include_short_address=address_raw.get('roadAddr').replace(full_state, short_state),

            # --- 🚀 위치 및 공간 정보 (데이터 없으면 null) ---
            latitude=float(center_pt.y) if center_pt else None,
            longitude=float(center_pt.x) if center_pt else None,
            geo_point={
                "type": "Point",
                "coordinates": [float(center_pt.x), float(center_pt.y)]
            } if center_pt else None,
            geometry=merged_geometry,
        )

    def _process_geometries(self, continuous_items: List[Dict]) -> Tuple[Optional[Dict], Optional[Point]]:
        """폴리곤 병합 및 중앙점(Centroid) 계산"""
        if not continuous_items:
            return None, None

        valid_shapes = []
        for item in continuous_items:
            geom = item.get('geometry')
            if not geom: continue
            try:
                s = shape(geom)
                if not s.is_valid:
                    s = s.buffer(0)
                valid_shapes.append(s)
            except:
                continue

        if not valid_shapes:
            return None, None

        try:
            merged_shape = unary_union(valid_shapes)
            return mapping(merged_shape), merged_shape.centroid
        except:
            first_shape = valid_shapes[0]
            return mapping(first_shape), first_shape.centroid

    def _process_related_blocks(self, rel_jibun: Any, state_name: str, district_name: str, township_name: str) -> List[str]:
        """관련 지번 리스트 가공 로직"""
        if not rel_jibun:
            return []

        # 문자열로 들어올 경우 리스트화
        blocks = rel_jibun.split(',') if isinstance(rel_jibun, str) else rel_jibun

        results = []
        for b in blocks:
            clean_b = b.strip()
            if not clean_b: continue

            parts = []
            if state_name not in clean_b: parts.append(state_name)
            if district_name not in clean_b: parts.append(district_name)
            if district_name not in clean_b: parts.append(township_name)
            parts.append(clean_b)
            results.append(' '.join(parts))
        return results

    def _combine_num(self, main: Any, sub: Any) -> str:
        """본번-부번 결합 (예: 123, 0 -> 123 / 123, 1 -> 123-1)"""
        m = str(main or '').strip()
        s = str(sub or '').strip()
        if not m: return ""
        return m if not s or s == '0' else f"{m}-{s}"

    def _to_int(self, value: Any) -> Optional[int]:
        try:
            if value is None: return None
            v = str(value).strip()
            return int(v) if v.isdigit() else None
        except:
            return None