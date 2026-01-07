from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_vworld_driver \
    import (ContinuousGeometryVworldDriver)
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_mongodb_driver \
    import (ContinuousGeometryMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class ContinuousGeometryManager(AbstractManager):
    _vworld_driver: ContinuousGeometryVworldDriver
    _mongodb_driver: ContinuousGeometryMongodbDriver

    def __init__(self, mongodb_driver: ContinuousGeometryMongodbDriver, vworld_driver: ContinuousGeometryVworldDriver):
        self._mongodb_driver = mongodb_driver
        self._vworld_driver = vworld_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def jgk_driver(self) -> DriverInterface:
        return self._vworld_driver

    def _create_vworld_driver(self) -> DriverInterface:
        return self._vworld_driver