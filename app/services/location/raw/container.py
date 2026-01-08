from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.location.raw.drivers.address.address_jgk_driver import AddressJgkDriver
from app.services.location.raw.drivers.address.address_mongodb_driver import AddressMongodbDriver
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_mongodb_driver import \
    ContinuousGeometryMongodbDriver
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_vworld_driver import \
    ContinuousGeometryVworldDriver
from app.services.location.raw.drivers.point_geometry.point_geometry_mongodb_driver import PointGeometryMongodbDriver
from app.services.location.raw.drivers.point_geometry.point_geometry_vworld_driver import PointGeometryVworldDriver
from app.services.location.raw.managers.address_manager import AddressManager
from app.services.location.raw.managers.continuous_geometry_manager import ContinuousGeometryManager
from app.services.location.raw.managers.point_geometry_manager import PointGeometryManager
from app.services.location.raw.services.address_service import AddressService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService


class RawContainer(AbstractContainer):
    address_jgk_driver: AddressJgkDriver = providers.Factory(AddressJgkDriver)
    address_mongodb_driver: AddressMongodbDriver = providers.Factory(AddressMongodbDriver)
    address_manager: AddressManager = providers.Singleton(
        AddressManager,
        jgk_driver=address_jgk_driver,
        mongodb_driver=address_mongodb_driver,
    )
    address_service: AddressService = providers.Singleton(AddressService, manager=address_manager)

    continuous_geometry_vworld_driver: ContinuousGeometryVworldDriver = providers.Factory(ContinuousGeometryVworldDriver)
    continuous_geometry_mongodb_driver: ContinuousGeometryMongodbDriver = providers.Factory(ContinuousGeometryMongodbDriver)
    continuous_geometry_manager: ContinuousGeometryManager = providers.Singleton(
        ContinuousGeometryManager,
        vworld_driver=continuous_geometry_vworld_driver,
        mongodb_driver=continuous_geometry_mongodb_driver,
    )
    continuous_geometry_service: ContinuousGeometryService = providers.Singleton(ContinuousGeometryService, manager=continuous_geometry_manager)

    point_geometry_vworld_driver: PointGeometryVworldDriver = providers.Factory(PointGeometryVworldDriver)
    point_geometry_mongodb_driver: PointGeometryMongodbDriver = providers.Factory(PointGeometryMongodbDriver)
    point_geometry_manager: PointGeometryManager = providers.Singleton(
        PointGeometryManager,
        vworld_driver=point_geometry_vworld_driver,
        mongodb_driver=point_geometry_mongodb_driver,
    )
    point_geometry_service: PointGeometryService = providers.Singleton(PointGeometryService, manager=point_geometry_manager)


