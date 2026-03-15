from app.services.building.raw.services.basic_info_service import BasicInfoService
from app.services.building.raw.services.group_info_service import GroupInfoService
from app.services.building.raw.services.title_info_service import TitleInfoService
from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.managers.complex_manager import ComplexManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.building.structure.services.address_service import AddressService
from app.services.location.boundary.dto import BoundaryItemDto
from app.services.location.boundary.service import BoundaryService
from app.services.building.structure.handlers.complex_dto_handler import ComplexDtoHandler
from app.services.building.structure.dtos.address_dto import AddressDto
from app.services.building.structure.dtos.complex_dto import ComplexDto
from typing import Optional, Dict, Any, List, Union
from app.core.helpers.log import Log


class ComplexService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self,
         manager: ComplexManager,
         complex_dto_handler: ComplexDtoHandler,
         address_service: AddressService,
         basic_info_service: BasicInfoService,
         group_info_service: GroupInfoService,
         title_info_service: TitleInfoService):
        self._manager = manager
        self.complex_dto_handler = complex_dto_handler
        self._address_service = address_service
        self._basic_info_service = basic_info_service
        self._group_info_service = group_info_service
        self._title_info_service = title_info_service

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
