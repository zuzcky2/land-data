from app.services.building.raw.managers.abstract_manager import AbstractManager
from app.services.building.raw.drivers.title_info.title_info_mongodb \
    import (TitleInfoMongodbDriver)
from app.services.building.raw.drivers.title_info.title_info_dgk \
    import (TitleInfoDgkDriver)
from app.services.building.raw.drivers.driver_interface \
    import (DriverInterface)


class TitleInfoManager(AbstractManager):
    _mongodb_driver: TitleInfoMongodbDriver
    _dgk_driver: TitleInfoDgkDriver

    def __init__(self, mongodb_driver: TitleInfoMongodbDriver, dgk_driver: TitleInfoDgkDriver):
        self._mongodb_driver = mongodb_driver
        self._dgk_driver = dgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def dgk_driver(self) -> DriverInterface:
        return self._dgk_driver


