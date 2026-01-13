from typing import Optional, Dict, Any
from datetime import datetime
from app.services.building.structure.dtos.address_dto import AddressDto
from app.services.building.structure.dtos.complex_dto import ComplexDto


class ComplexDtoHandler:

    def handle(self, address_dto: AddressDto, complex_type: str, raw_data: Dict[str, Any]) -> Optional[ComplexDto]:
        if not raw_data:
            return None

        # 1. 날짜 정보 전처리
        permit_date = self._parse_date(raw_data.get('pmsDay'))
        construction_date = self._parse_date(raw_data.get('stcnsDay'))
        approval_date = self._parse_date(raw_data.get('useAprDay'))
        display_date, display_date_name = self._get_display_date(approval_date, construction_date, permit_date)

        # 2. 주차 정보 전처리 (옥내/옥외 합산)
        indoor_parking = int(raw_data.get('indrAutoUtcnt') or 0) + int(raw_data.get('indrMechUtcnt') or 0)
        outdoor_parking = int(raw_data.get('oudrAutoUtcnt') or 0) + int(raw_data.get('oudrMechUtcnt') or 0)

        # [추가] etcPurps 가공 로직
        raw_etc_purpose = raw_data.get('etcPurps', '')
        purpose_list = []
        if raw_etc_purpose and str(raw_etc_purpose).strip():
            # 콤마로 분리 -> 양쪽 공백 제거 -> 빈 문자열 제외 -> 리스트 생성
            purpose_list = [p.strip() for p in str(raw_etc_purpose).split(',') if p.strip()]

        # 3. DTO 생성 (ComplexDto 필드만 사용)
        return ComplexDto(
            building_manage_number=address_dto.building_manage_number,
            address_id=address_dto.id,  # address_dto의 _id 필드 매핑
            item_name=raw_data.get('bldNm', '').strip() or address_dto.building_name,
            register_kind_code=raw_data.get('regstrKindCdNm', ''),

            # 규모 및 면적
            land_area=float(raw_data.get('platArea') or 0),
            building_area=float(raw_data.get('archArea') or 0),
            total_floor_area=float(raw_data.get('totArea') or 0),
            building_coverage_ratio=float(raw_data.get('bcRat') or 0),
            floor_area_ratio=float(raw_data.get('vlRat') or 0),
            main_building_count=int(raw_data.get('mainBldCnt') or 1),
            annex_building_count=int(raw_data.get('atchBldCnt') or 0),

            # 세대 및 가구
            household_count=int(raw_data.get('hhldCnt') or 0),
            family_count=int(raw_data.get('fmlyCnt') or 0),
            unit_count=int(raw_data.get('hoCnt') or 0),
            display_count=int(raw_data.get('hhldCnt') or raw_data.get('fmlyCnt') or raw_data.get('hoCnt') or 0),

            # 주차 정보
            total_parking_count=int(raw_data.get('totPkngCnt') or 0),
            indoor_parking_count=indoor_parking,
            outdoor_parking_count=outdoor_parking,

            # 주요 용도
            main_purpose_name=raw_data.get('mainPurpsCdNm'),
            etc_purpose_name=purpose_list,

            # 날짜 정보
            permit_date=permit_date,
            construction_date=construction_date,
            approval_date=approval_date,
            display_date_name=display_date_name,
            display_date=display_date,

            # 인허가 정보
            permit_authority=raw_data.get('pmsnoKikCdNm'),
            permit_year=self._parse_date(raw_data.get('pmsnoYear'), "%Y") if str(
                raw_data.get('pmsnoYear')).strip() else None
        )

    def _parse_date(self, date_str: Any, date_format: str = "%Y%m%d") -> Optional[datetime]:
        if not date_str or str(date_str).strip() in ['', '0', 'None']:
            return None
        try:
            return datetime.strptime(str(date_str).strip(), date_format)
        except ValueError:
            return None

    def _get_display_date(self, approval: Optional[datetime], construction: Optional[datetime],
                          permit: Optional[datetime]):
        if approval: return approval, "사용승인일"
        if construction: return construction, "착공일"
        if permit: return permit, "허가일"
        return None, None