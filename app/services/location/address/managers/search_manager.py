from app.services.location.address.managers.abstract_manager import AbstractManager
from app.services.location.address.drivers.search.search_jgk_driver \
    import (SearchJgkDriver)
from app.services.location.address.drivers.search.search_mongodb_driver \
    import (SearchMongodbDriver)
from app.services.location.address.drivers.driver_interface \
    import (DriverInterface)


class SearchManager(AbstractManager):
    _jgk_driver: SearchJgkDriver
    _mongodb_driver: SearchMongodbDriver

    def __init__(self, mongodb_driver: SearchMongodbDriver, jgk_driver: SearchJgkDriver):
        self._mongodb_driver = mongodb_driver
        self._jgk_driver = jgk_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def jgk_driver(self) -> DriverInterface:
        return self._jgk_driver
