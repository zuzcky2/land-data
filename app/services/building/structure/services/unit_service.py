from typing import Optional, Dict, Any
from app.services.building.structure.managers.unit_manager import UnitManager
from app.services.building.structure.managers.building_manager import BuildingManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.building.structure.handlers.unit_dto_handler import UnitDtoHandler
from app.services.building.structure.dtos.unit_dto import UnitDto
from app.services.building.raw.services.area_info_service import AreaInfoService
from app.core.helpers.log import Log


class UnitService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self, manager: UnitManager, unit_dto_handler: UnitDtoHandler,
                 building_manager: BuildingManager, area_info_service: AreaInfoService):
        self._manager = manager
        self.unit_dto_handler = unit_dto_handler
        self._building_manager = building_manager
        self._area_info_service = area_info_service

    @property
    def logger_name(self) -> str:
        return 'building_structure_unit'

    @property
    def manager(self) -> UnitManager:
        return self._manager

    def build_by_basic_info(self, basic_raw: Dict[str, Any]) -> Optional[UnitDto]:
        """
        basic_info(전유부, regstrKindCd=4) 레코드로 units 컬렉션 레코드를 생성/갱신합니다.
        mgmUpBldrgstPk → buildings에서 building_manage_number 조회.
        mgmBldrgstPk → area_info에서 호실명/용도 보완.
        """
        mgm_pk = basic_raw.get('mgmBldrgstPk')
        mgm_up_pk = basic_raw.get('mgmUpBldrgstPk')
        if not mgm_pk or not mgm_up_pk:
            return None

        try:
            building = self._building_manager.driver(self.DRIVER_MONGODB).set_arguments({
                'register_manage_number': str(mgm_up_pk)
            }).read_one()

            if not building:
                return None

            building_manage_number = building.get('building_manage_number')
            if not building_manage_number:
                return None

            area_raw = self._area_info_service.get_detail({'mgmBldrgstPk': str(mgm_pk)})

            dto = self.unit_dto_handler.handle(basic_raw, building_manage_number, area_raw)
            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])
            return dto
        except Exception as e:
            Log.get_logger(self.logger_name).error(
                f"Build Error [{mgm_pk}]: {str(e)}", exc_info=True
            )
            return None
