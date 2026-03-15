from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.building.structure.drivers.address.address_mongodb_driver import AddressMongodbDriver
from app.services.building.structure.drivers.complex.complex_mongodb_driver import ComplexMongodbDriver
from app.services.building.structure.drivers.building.building_mongodb_driver import BuildingMongodbDriver
from app.services.building.structure.drivers.floor.floor_mongodb_driver import FloorMongodbDriver
from app.services.building.structure.drivers.unit.unit_mongodb_driver import UnitMongodbDriver
from app.services.building.structure.handlers.address_dto_handler import AddressDtoHandler
from app.services.building.structure.handlers.building_classifier_handler import BuildingClassifierHandler
from app.services.building.structure.handlers.complex_dto_handler import ComplexDtoHandler
from app.services.building.structure.handlers.building_dto_handler import BuildingDtoHandler
from app.services.building.structure.handlers.floor_dto_handler import FloorDtoHandler
from app.services.building.structure.handlers.unit_dto_handler import UnitDtoHandler
from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.managers.complex_manager import ComplexManager
from app.services.building.structure.managers.building_manager import BuildingManager
from app.services.building.structure.managers.floor_manager import FloorManager
from app.services.building.structure.managers.unit_manager import UnitManager
from app.services.building.structure.services.address_service import AddressService
from app.services.building.structure.services.complex_service import ComplexService
from app.services.building.structure.services.building_service import BuildingService
from app.services.building.structure.services.floor_service import FloorService
from app.services.building.structure.services.unit_service import UnitService
from app.services.location.raw.container import RawContainer as LocationRawContainer
from app.services.building.raw.container import RawContainer as BuildingRawContainer
from app.services.location.boundary.container import BoundaryContainer


class StructureContainer(AbstractContainer):
    # 타 컨테이너 참조
    location_raw: LocationRawContainer = providers.Container(LocationRawContainer)
    building_raw: BuildingRawContainer = providers.Container(BuildingRawContainer)
    boundary: BoundaryContainer = providers.Container(BoundaryContainer)

    building_classifier_handler = providers.Singleton(BuildingClassifierHandler)

    # ── Address ──────────────────────────────────────────────────────────────
    address_mongodb_driver: AddressMongodbDriver = providers.Factory(AddressMongodbDriver)
    address_manager: AddressManager = providers.Singleton(AddressManager, mongodb_driver=address_mongodb_driver)
    address_dto_handler: AddressDtoHandler = providers.Singleton(AddressDtoHandler)
    address_service: AddressService = providers.Singleton(
        AddressService,
        manager=address_manager,
        address_dto_handler=address_dto_handler,
        boundary_service=boundary.boundary_service,
        raw_road_address_service=location_raw.road_address_service,
        raw_road_code_service=location_raw.road_code_service,
        raw_block_address_service=location_raw.block_address_service,
        raw_building_group_service=location_raw.building_group_service,
        raw_point_geometry_service=location_raw.point_geometry_service,
        raw_continuous_geometry_service=location_raw.continuous_geometry_service
    )

    # ── Complex ──────────────────────────────────────────────────────────────
    complex_mongodb_driver: ComplexMongodbDriver = providers.Factory(ComplexMongodbDriver)
    complex_manager: ComplexManager = providers.Singleton(
        ComplexManager,
        mongodb_driver=complex_mongodb_driver
    )
    complex_dto_handler: ComplexDtoHandler = providers.Singleton(
        ComplexDtoHandler,
        building_classifier_handler=building_classifier_handler,
    )
    complex_service: ComplexService = providers.Singleton(
        ComplexService,
        manager=complex_manager,
        complex_dto_handler=complex_dto_handler,
        address_service=address_service,
        basic_info_service=building_raw.basic_info_service,
        group_info_service=building_raw.group_info_service,
        title_info_service=building_raw.title_info_service
    )

    # ── Building ─────────────────────────────────────────────────────────────
    building_mongodb_driver: BuildingMongodbDriver = providers.Factory(BuildingMongodbDriver)
    building_manager: BuildingManager = providers.Singleton(
        BuildingManager,
        mongodb_driver=building_mongodb_driver
    )
    building_dto_handler: BuildingDtoHandler = providers.Singleton(BuildingDtoHandler)
    building_service: BuildingService = providers.Singleton(
        BuildingService,
        manager=building_manager,
        building_dto_handler=building_dto_handler,
    )

    # ── Floor ─────────────────────────────────────────────────────────────────
    floor_mongodb_driver: FloorMongodbDriver = providers.Factory(FloorMongodbDriver)
    floor_manager: FloorManager = providers.Singleton(
        FloorManager,
        mongodb_driver=floor_mongodb_driver
    )
    floor_dto_handler: FloorDtoHandler = providers.Singleton(FloorDtoHandler)
    floor_service: FloorService = providers.Singleton(
        FloorService,
        manager=floor_manager,
        floor_dto_handler=floor_dto_handler,
        building_manager=building_manager,
    )

    # ── Unit ──────────────────────────────────────────────────────────────────
    unit_mongodb_driver: UnitMongodbDriver = providers.Factory(UnitMongodbDriver)
    unit_manager: UnitManager = providers.Singleton(
        UnitManager,
        mongodb_driver=unit_mongodb_driver
    )
    unit_dto_handler: UnitDtoHandler = providers.Singleton(UnitDtoHandler)
    unit_service: UnitService = providers.Singleton(
        UnitService,
        manager=unit_manager,
        unit_dto_handler=unit_dto_handler,
        building_manager=building_manager,
        area_info_service=building_raw.area_info_service,
    )
