from typing import Optional, Dict, Any
from app.services.building.structure.managers.building_manager import BuildingManager
from app.services.building.structure.services.abstract_service import AbstractService
from app.services.building.structure.handlers.building_dto_handler import BuildingDtoHandler
from app.services.building.structure.dtos.building_dto import BuildingDto
from app.core.helpers.log import Log


class BuildingService(AbstractService):
    DRIVER_MONGODB: str = 'mongodb'

    def __init__(self, manager: BuildingManager, building_dto_handler: BuildingDtoHandler):
        self._manager = manager
        self.building_dto_handler = building_dto_handler

    @property
    def logger_name(self) -> str:
        return 'building_structure_building'

    @property
    def manager(self) -> BuildingManager:
        return self._manager

    def build_by_title_info(self, title_raw: Dict[str, Any]) -> Optional[BuildingDto]:
        """
        title_info(표제부, regstrKindCd=3) 레코드로 buildings 컬렉션 레코드를 생성/갱신합니다.
        """
        mgm_pk = title_raw.get('mgmBldrgstPk')
        if not mgm_pk:
            return None

        try:
            dto = self.building_dto_handler.handle(title_raw)
            if dto:
                self.manager.driver(self.DRIVER_MONGODB).store([dto.dict()])
            return dto
        except Exception as e:
            Log.get_logger(self.logger_name).error(
                f"Build Error [{mgm_pk}]: {str(e)}", exc_info=True
            )
            return None
