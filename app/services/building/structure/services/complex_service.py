import re
from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.group_info_service import GroupInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService
from app.services.building.raw.services.kapt_basic_service import KaptBasicService
from app.services.building.raw.services.kapt_detail_service import KaptDetailService
from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.managers.complex_manager import ComplexManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.building.structure.services.address_service import AddressService
from app.services.building.structure.handlers.complex_dto_handler import ComplexDtoHandler
from app.services.building.structure.dtos.address_dto import AddressDto
from app.services.building.structure.dtos.complex_dto import ComplexDto
from typing import Optional, Dict, Any, List, Union
from datetime import datetime
from app.core.helpers.log import Log


class ComplexService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self,
         manager: ComplexManager,
         complex_dto_handler: ComplexDtoHandler,
         address_service: AddressService,
         basic_info_service: BasicInfoService,
         group_info_service: GroupInfoService,
         title_info_service: TitleInfoService,
         kapt_basic_service: KaptBasicService,
         kapt_detail_service: KaptDetailService):
        self._manager = manager
        self.complex_dto_handler = complex_dto_handler
        self._address_service = address_service
        self._basic_info_service = basic_info_service
        self._group_info_service = group_info_service
        self._title_info_service = title_info_service
        self._kapt_basic_service = kapt_basic_service
        self._kapt_detail_service = kapt_detail_service

    @property
    def logger_name(self) -> str:
        return 'building_structure_complex'

    @property
    def manager(self) -> ComplexManager:
        return self._manager

    def build_by_bd_mgt_sn(self, building_manage_number: str) -> Optional[ComplexDto]:
        address_item = self._address_service.manager.driver('mongodb').set_arguments({
            'building_manage_number': building_manage_number
        }).read_one()
        if not address_item:
            Log.get_logger(self.logger_name).warning(f"Address not found for bdMgtSn: {building_manage_number}")
            return None

        return self._run_build_pipeline(AddressDto(**address_item))

    def build_by_address(self, address_dto: Union[dict, AddressDto]) -> Optional[ComplexDto]:
        if isinstance(address_dto, dict):
            address_dto = AddressDto(**address_dto)
        return self._run_build_pipeline(address_dto)

    def _run_build_pipeline(self, address_dto: AddressDto):
        """
        bdMgtSn 기준 복합 단지 생성. 우선순위: 총괄표제부(1) > 일반건축물(2).
        표제부(3)는 건물(buildings) 컬렉션 대상이므로 여기서는 처리하지 않음.
        """
        try:
            bd_mgt_sn = address_dto.building_manage_number

            # 1순위: 총괄표제부(regstrKindCd=1)
            group_basic = self._basic_info_service.get_detail({
                'bdMgtSn': bd_mgt_sn,
                'regstrKindCd': '1',
                'dead': {'$ne': True}
            })

            if group_basic:
                raw = self._group_info_service.get_detail({
                    'mgmBldrgstPk': group_basic.get('mgmBldrgstPk')
                })
                complex_type = 'group'
            else:
                # 2순위: 일반건축물(regstrKindCd=2)
                title_basic = self._basic_info_service.get_detail({
                    'bdMgtSn': bd_mgt_sn,
                    'regstrKindCd': '2',
                    'dead': {'$ne': True}
                })
                if not title_basic:
                    return None
                raw = self._title_info_service.get_detail({
                    'mgmBldrgstPk': title_basic.get('mgmBldrgstPk')
                })
                complex_type = 'title'

            if raw:
                dto = self.complex_dto_handler.handle(address_dto, complex_type, raw)
                if dto:
                    self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])
                    return dto
            return None

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"Build Pipeline Error [{address_dto.building_manage_number}]: {str(e)}")
            return None

    def sync_kapt(self, kapt_basic: Dict[str, Any]) -> bool:
        """
        K-APT 단지 1건을 addresses → complexes에 매칭하여 kapt 필드를 $set으로 병합합니다.
        매칭 키: doroJuso → addresses.road_name + road_main + road_sub
        """
        kapt_code = kapt_basic.get('kaptCode')
        doro_juso = str(kapt_basic.get('doroJuso') or '').strip()
        if not kapt_code or not doro_juso:
            return False

        try:
            road_name, road_main, road_sub = self._parse_doro_juso(doro_juso)
            if not road_name or not road_main:
                return False

            # 1. addresses에서 도로명 + 번지로 매칭
            addr_query: Dict[str, Any] = {'road_name': road_name, 'road_main': road_main}
            if road_sub and road_sub != '0':
                addr_query['road_sub'] = road_sub

            address = self._address_service.manager.driver(self.DRIVER_MONGODB).set_arguments(addr_query).read_one()
            if not address:
                return False

            bd_mgt_sn = address.get('building_manage_number')
            if not bd_mgt_sn:
                return False

            # 2. kapt_detail 조회
            kapt_detail = self._kapt_detail_service.get_detail({'kaptCode': kapt_code}) or {}

            # 3. 병합할 kapt 필드만 추출 (None은 제외하여 기존 값 보호)
            ev_count = (int(kapt_detail.get('groundElChargerCnt') or 0) +
                        int(kapt_detail.get('undergroundElChargerCnt') or 0))

            def _int(v):
                try: return int(v) if v not in (None, '', 'None') else None
                except: return None

            kapt_patch = {k: v for k, v in {
                'kapt_code': kapt_code,
                'kapt_name': kapt_basic.get('kaptName'),
                'heating_type': kapt_basic.get('codeHeatNm') or None,
                'area_60_count': _int(kapt_basic.get('kaptMparea60')),
                'area_85_count': _int(kapt_basic.get('kaptMparea85')),
                'area_135_count': _int(kapt_basic.get('kaptMparea135')),
                'area_136_count': _int(kapt_basic.get('kaptMparea136')),
                'management_company': kapt_basic.get('kaptAcompany') or None,
                'elevator_count': _int(kapt_detail.get('kaptdEcnt')),
                'parking_count_kapt': _int(kapt_detail.get('kaptdPcnt')),
                'subway_station': kapt_detail.get('subwayStation') or None,
                'subway_line': kapt_detail.get('subwayLine') or None,
                'bus_walktime': _int(kapt_detail.get('kaptdWtimebus')),
                'subway_walktime': _int(kapt_detail.get('kaptdWtimesub')),
                'convenient_facility': kapt_detail.get('convenientFacility') or None,
                'education_facility': kapt_detail.get('educationFacility') or None,
                'welfare_facility': kapt_detail.get('welfareFacility') or None,
                'ev_charger_count': ev_count if ev_count else None,
            }.items() if v is not None}

            if not kapt_patch:
                return False

            kapt_patch['updated_at'] = datetime.now()

            # 4. $set으로 부분 업데이트 (기존 필드 보호)
            self.manager.driver(self.DRIVER_MONGODB).collection.update_one(
                {'building_manage_number': bd_mgt_sn},
                {'$set': kapt_patch}
            )
            return True

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"KaptSync Error [{kapt_code}]: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def _parse_doro_juso(doro_juso: str):
        """도로명주소에서 도로명, 본번, 부번을 추출합니다.
        예: '서울특별시 강남구 강남대로 396' → ('강남대로', '396', '0')
        """
        m = re.search(r'([가-힣0-9]+(?:대로|로|길))\s+(\d+)(?:-(\d+))?', doro_juso)
        if m:
            return m.group(1), m.group(2), m.group(3) or '0'
        return None, None, None
