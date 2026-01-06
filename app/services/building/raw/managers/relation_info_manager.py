from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.relation_info.relation_info_dgk \
    import (RelationInfoDgkDriver)
from app.services.building.raw.drivers.relation_info.relation_info_mongodb \
    import (RelationInfoMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class RelationInfoManager(AbstractManager):
    _mongodb_driver: RelationInfoMongodbDriver
    _dgk_driver: RelationInfoDgkDriver

    def __init__(self, mongodb_driver: RelationInfoMongodbDriver, dgk_driver: RelationInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
