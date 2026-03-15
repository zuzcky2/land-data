from typing import Optional, Dict, Any
from app.services.building.structure.managers.floor_manager import FloorManager
from app.services.building.structure.managers.building_manager import BuildingManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.building.structure.handlers.floor_dto_handler import FloorDtoHandler
from app.services.building.structure.dtos.floor_dto import FloorDto
from app.core.helpers.log import Log


class FloorService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self, manager: FloorManager, floor_dto_handler: FloorDtoHandler,
                 building_manager: BuildingManager):
        self._manager = manager
        self.floor_dto_handler = floor_dto_handler
        self._building_manager = building_manager

    @property
    def logger_name(self) -> str:
        return 'building_structure_floor'

    @property
    def manager(self) -> FloorManager:
        return self._manager

    def build_by_floor_info(self, floor_raw: Dict[str, Any]) -> Optional[FloorDto]:
        """
        floor_info 레코드로 floors 컬렉션 레코드를 생성/갱신합니다.
        mgmBldrgstPk → buildings 컬렉션에서 building_manage_number(bdMgtSn) 조회.
        """
        mgm_pk = floor_raw.get('mgmBldrgstPk')
        if not mgm_pk:
            return None

        try:
            building = self._building_manager.driver(self.DRIVER_MONGODB).set_arguments({
                'register_manage_number': str(mgm_pk)
            }).read_one()

            if not building:
                return None

            building_manage_number = building.get('building_manage_number')
            if not building_manage_number:
                return None

            dto = self.floor_dto_handler.handle(floor_raw, building_manage_number)
            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])
            return dto
        except Exception as e:
            Log.get_logger(self.logger_name).error(
                f"Build Error [{mgm_pk}]: {str(e)}", exc_info=True
            )
            return None
