from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.point_geometry.point_geometry_vworld_driver \
    import (PointGeometryVworldDriver)
from app.services.location.raw.drivers.point_geometry.point_geometry_mongodb_driver \
    import (PointGeometryMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class PointGeometryManager(AbstractManager):
    _vworld_driver: PointGeometryVworldDriver
    _mongodb_driver: PointGeometryMongodbDriver

    def __init__(self, mongodb_driver: PointGeometryMongodbDriver, vworld_driver: PointGeometryVworldDriver):
        self._mongodb_driver = mongodb_driver
        self._vworld_driver = vworld_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def vworld_driver(self) -> DriverInterface:
        return self._vworld_driver

    def _create_vworld_driver(self) -> DriverInterface:
        return self._vworld_driver