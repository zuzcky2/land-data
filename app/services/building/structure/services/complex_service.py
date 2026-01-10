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
from typing import Optional, Dict, Any, List
from app.core.helpers.log import Log


class ComplexService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self,
         manager: ComplexManager,
         complex_dto_handler: ComplexDtoHandler,
         address_service: AddressService,
         group_info_service: GroupInfoService,
         title_info_service: TitleInfoService):
        self._manager = manager
        self.complex_dto_handler = complex_dto_handler
        self._address_service = address_service
        self._group_info_service = group_info_service
        self._title_info_service = title_info_service

    @property
    def logger_name(self) -> str:
        return 'building_structure_complex'

    @property
    def manager(self) -> ComplexManager:
        return self._manager

    def build_by_bd_mgt_sn(self, building_manager_number: str) -> Optional[ComplexDto]:
        address_item = self._.get_detail({'building_manager_number': building_manager_number})
        if not address_item:
            Log.get_logger(self.logger_name).warning(f"Raw address not found for: {building_manager_number}")
            return None

        return self._run_build_pipeline(AddressDto(**address_item))

    def build_by_address(self, address_dto: AddressDto) -> Optional[ComplexDto]:

        return self._run_build_pipeline(address_dto)

    def _run_build_pipeline(self, address_dto: AddressDto) -> Optional[ComplexDto]:
        try:
            complex_type = 'group'
            building_params = {'bdMgtSn': address_dto.building_manage_number, 'dead': {'$ne': True}}

            building = self._group_info_service.get_detail(building_params)

            if not building:
                complex_type = 'title'
                building = self._title_info_service.get_detail(building_params)

            dto = self.complex_dto_handler.handle(address_dto, complex_type, building)

            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])

            return dto

        except Exception as e:
            Log.get_logger(self.logger_name).error(f"Build Pipeline Error [{address_dto.building_manage_number}]: {str(e)}")
            return None
