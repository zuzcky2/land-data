from typing import Optional, Dict, Any
from datetime import datetime
from app.services.building.structure.dtos.building_dto import BuildingDto


class BuildingDtoHandler:

    def handle(self, title_raw: Dict[str, Any]) -> Optional[BuildingDto]:
        if not title_raw:
            return None

        bd_mgt_sn = title_raw.get('bdMgtSn')
        mgm_pk = title_raw.get('mgmBldrgstPk')
        if not bd_mgt_sn or not mgm_pk:
            return None

        return BuildingDto(
            register_manage_number=str(mgm_pk),
            building_manage_number=str(bd_mgt_sn),

            dong_name=str(title_raw.get('dongNm') or '').strip() or None,
            main_purpose=str(title_raw.get('mainPurpsCdNm') or '').strip() or None,
            sub_purpose=str(title_raw.get('etcPurps') or '').strip() or None,
            structure=str(title_raw.get('strctCdNm') or '').strip() or None,
            roof=str(title_raw.get('roofCdNm') or '').strip() or None,

            ground_floor_count=int(title_raw.get('grndFlrCnt') or 0),
            underground_floor_count=int(title_raw.get('ugrndFlrCnt') or 0),
            height=float(title_raw.get('heit')) if title_raw.get('heit') else None,

            total_area=float(title_raw.get('totArea') or 0),
            building_area=float(title_raw.get('archArea') or 0),
            annex_area=float(title_raw.get('atchBldArea') or 0),

            household_count=int(title_raw.get('hhldCnt') or 0),
            family_count=int(title_raw.get('fmlyCnt') or 0),
            unit_count=int(title_raw.get('hoCnt') or 0),

            is_main_building=(str(title_raw.get('mainAtchGbCd') or '0') == '0'),

            permit_date=self._parse_date(title_raw.get('pmsDay')),
            construction_date=self._parse_date(title_raw.get('stcnsDay')),
            approval_date=self._parse_date(title_raw.get('useAprDay')),
        )

    def _parse_date(self, date_str: Any) -> Optional[datetime]:
        if not date_str or str(date_str).strip() in ['', '0', 'None']:
            return None
        try:
            return datetime.strptime(str(date_str).strip(), '%Y%m%d')
        except ValueError:
            return None
