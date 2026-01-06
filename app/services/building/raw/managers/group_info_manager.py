from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.group_info.group_info_dgk \
    import (GroupInfoDgkDriver)
from app.services.building.raw.drivers.group_info.group_info_mongodb \
    import (GroupInfoMongodbDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class GroupInfoManager(AbstractManager):
    _mongodb_driver: GroupInfoMongodbDriver
    _dgk_driver: GroupInfoDgkDriver

    def __init__(self, mongodb_driver: GroupInfoMongodbDriver, dgk_driver: GroupInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver
