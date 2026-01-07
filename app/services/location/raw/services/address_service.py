
from app.services.location.raw.managers.address_manager import AddressManager
from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.services.abstract_service import AbstractService
from typing import Dict, Any, Optional
from app.core.helpers.log import Log


class AddressService(AbstractService):

    def __init__(self, manager: AddressManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_address'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

    def get_detail_by_chain(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        mongodb_driver = self.manager.driver(self.DRIVER_MONGODB)
        item = mongodb_driver.clear().set_arguments(params).read_one()

        if not item:
            jgk_driver = self.manager.driver(self.DRIVER_JGK)

            item = jgk_driver.clear().set_arguments(params).read_one()

            if item:
                mongodb_driver.store([item])
                return item

        return None

    def sync_from_jgk(self, params: Dict[str, Any], source: str = 'group') -> Dict[str, Any]:
        # 소스별로 다른 로거 사용 (building_raw_group, building_raw_title)
        current_logger = Log.get_logger(f"{self.logger_name}_{source}")
        current_logger.info(f"Sync Start: {params}")

        try:
            item = (
                self.manager.driver(self.DRIVER_JGK)
                .clear()
                .set_arguments(params)
                .set_pagination(page=1, per_page=1)
                .read_one()
            )

            if item:
                self.manager.driver(self.DRIVER_MONGODB).store([item])
                return {'status': 'success', 'bdMgtSn': item.get('bdMgtSn')}
            else:
                return {'status': 'fail', 'dead': True}

        except Exception as e:
            current_logger.error(f"[SYNC_STOP_ERROR] | Message: {str(e)} | Params: {str(params)}")
            raise e
