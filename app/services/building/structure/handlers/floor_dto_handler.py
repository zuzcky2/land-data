from typing import Optional, Dict, Any
from app.services.building.structure.dtos.floor_dto import FloorDto


class FloorDtoHandler:

    def handle(self, floor_raw: Dict[str, Any], building_manage_number: str) -> Optional[FloorDto]:
        if not floor_raw:
            return None

        mgm_pk = floor_raw.get('mgmBldrgstPk')
        flr_gb_cd = str(floor_raw.get('flrGbCd') or '')
        flr_no = floor_raw.get('flrNo')

        if not mgm_pk or flr_gb_cd == '' or flr_no is None:
            return None

        floor_id = f"{mgm_pk}_{flr_gb_cd}_{flr_no}"
        floor_type = '지하' if flr_gb_cd == '10' else '지상'

        return FloorDto(
            floor_id=floor_id,
            register_manage_number=str(mgm_pk),
            building_manage_number=building_manage_number,

            floor_type=floor_type,
            floor_type_code=flr_gb_cd,
            floor_number=int(flr_no),
            floor_name=str(floor_raw.get('flrNoNm') or '').strip(),

            area=float(floor_raw.get('area') or 0),
            main_purpose=str(floor_raw.get('mainPurpsCdNm') or '').strip() or None,
            sub_purpose=str(floor_raw.get('etcPurps') or '').strip() or None,
            is_main_building=(str(floor_raw.get('mainAtchGbCd') or '0') == '0'),
        )
