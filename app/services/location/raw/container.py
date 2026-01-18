from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.location.raw.drivers.address.address_jgk_driver import AddressJgkDriver
from app.services.location.raw.drivers.address.address_mongodb_driver import AddressMongodbDriver
from app.services.location.raw.drivers.block_address.block_address_mongodb_driver import BlockAddressMongodbDriver
from app.services.location.raw.drivers.block_address.block_address_text_driver import BlockAddressTextDriver
from app.services.location.raw.drivers.building_group.building_group_mongodb_driver import BuildingGroupMongodbDriver
from app.services.location.raw.drivers.building_group.building_group_text_driver import BuildingGroupTextDriver
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_mongodb_driver import \
    ContinuousGeometryMongodbDriver
from app.services.location.raw.drivers.continuous_geometry.continuous_geometry_vworld_driver import \
    ContinuousGeometryVworldDriver
from app.services.location.raw.drivers.point_geometry.point_geometry_mongodb_driver import PointGeometryMongodbDriver
from app.services.location.raw.drivers.point_geometry.point_geometry_vworld_driver import PointGeometryVworldDriver
from app.services.location.raw.drivers.road_address.road_address_mongodb_driver import RoadAddressMongodbDriver
from app.services.location.raw.drivers.road_address.road_address_text_driver import RoadAddressTextDriver
from app.services.location.raw.managers.address_manager import AddressManager
from app.services.location.raw.managers.block_address_manager import BlockAddressManager
from app.services.location.raw.managers.building_group_manager import BuildingGroupManager
from app.services.location.raw.managers.continuous_geometry_manager import ContinuousGeometryManager
from app.services.location.raw.managers.point_geometry_manager import PointGeometryManager
from app.services.location.raw.managers.road_address_manager import RoadAddressManager
from app.services.location.raw.services.address_db_download_service import AddressDBDownloadService
from app.services.location.raw.services.address_service import AddressService
from app.services.location.raw.services.block_address_service import BlockAddressService
from app.services.location.raw.services.building_group_service import BuildingGroupService
from app.services.location.raw.services.continuous_geometry_service import ContinuousGeometryService
from app.services.location.raw.services.point_geometry_service import PointGeometryService
from app.services.location.raw.services.road_address_service import RoadAddressService


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

    block_address_text_driver: BlockAddressTextDriver = providers.Factory(BlockAddressTextDriver)
    block_address_mongodb_driver: BlockAddressMongodbDriver = providers.Factory(BlockAddressMongodbDriver)
    block_address_manager: BlockAddressManager = providers.Singleton(
        BlockAddressManager,
        text_driver=block_address_text_driver,
        mongodb_driver=block_address_mongodb_driver,
    )
    block_address_service: BlockAddressService = providers.Singleton(BlockAddressService, manager=block_address_manager)

    road_address_text_driver: RoadAddressTextDriver = providers.Factory(RoadAddressTextDriver)
    road_address_mongodb_driver: RoadAddressMongodbDriver = providers.Factory(RoadAddressMongodbDriver)
    road_address_manager: RoadAddressManager = providers.Singleton(
        RoadAddressManager,
        text_driver=road_address_text_driver,
        mongodb_driver=road_address_mongodb_driver,
    )
    road_address_service: RoadAddressService = providers.Singleton(RoadAddressService, manager=road_address_manager)

    building_group_text_driver: BuildingGroupTextDriver = providers.Factory(BuildingGroupTextDriver)
    building_group_mongodb_driver: BuildingGroupMongodbDriver = providers.Factory(BuildingGroupMongodbDriver)
    building_group_manager: BuildingGroupManager = providers.Singleton(
        BuildingGroupManager,
        text_driver=building_group_text_driver,
        mongodb_driver=building_group_mongodb_driver
    )
    building_group_service: BuildingGroupService = providers.Singleton(BuildingGroupService, manager=building_group_manager)

    address_db_service: AddressDBDownloadService = providers.Singleton(AddressDBDownloadService)