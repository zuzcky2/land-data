from typing import Optional, Dict, Any
from app.services.building.structure.dtos.unit_dto import UnitDto


class UnitDtoHandler:

    def handle(self, basic_raw: Dict[str, Any], building_manage_number: str,
               area_raw: Optional[Dict[str, Any]] = None) -> Optional[UnitDto]:
        if not basic_raw:
            return None

        mgm_pk = basic_raw.get('mgmBldrgstPk')
        mgm_up_pk = basic_raw.get('mgmUpBldrgstPk')

        if not mgm_pk or not mgm_up_pk:
            return None

        # 호실명: area_info의 hoNm 우선, fallback bldNm
        unit_name = None
        if area_raw:
            unit_name = str(area_raw.get('hoNm') or '').strip() or None
        if not unit_name:
            unit_name = str(basic_raw.get('bldNm') or '').strip() or None

        main_purpose = None
        sub_purpose = None
        if area_raw:
            main_purpose = str(area_raw.get('mainPurpsCdNm') or '').strip() or None
            sub_purpose = str(area_raw.get('etcPurps') or '').strip() or None

        return UnitDto(
            register_manage_number=str(mgm_pk),
            parent_register_manage_number=str(mgm_up_pk),
            building_manage_number=building_manage_number,
            unit_name=unit_name,
            main_purpose=main_purpose,
            sub_purpose=sub_purpose,
            is_collective=(str(basic_raw.get('regstrGbCd') or '1') == '2'),
        )
