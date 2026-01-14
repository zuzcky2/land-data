from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.building.structure.drivers.address.address_mongodb_driver import AddressMongodbDriver
from app.services.building.structure.drivers.complex.complex_mongodb_driver import ComplexMongodbDriver
from app.services.building.structure.handlers.address_dto_handler import AddressDtoHandler
from app.services.building.structure.handlers.building_classifier_handler import BuildingClassifierHandler
from app.services.building.structure.handlers.complex_dto_handler import ComplexDtoHandler
from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.managers.complex_manager import ComplexManager
from app.services.building.structure.services.address_service import AddressService
from app.services.building.structure.services.complex_service import ComplexService
from app.services.location.raw.container import RawContainer as LocationRawContainer
from app.services.building.raw.container import RawContainer as BuildingRawContainer
from app.services.location.boundary.container import BoundaryContainer


class StructureContainer(AbstractContainer):
    # 타 컨테이너 참조
    location_raw: LocationRawContainer = providers.Container(LocationRawContainer)
    building_raw: BuildingRawContainer = providers.Container(BuildingRawContainer)
    boundary: BoundaryContainer = providers.Container(BoundaryContainer)

    building_classifier_handler = providers.Singleton(BuildingClassifierHandler)

    address_mongodb_driver: AddressMongodbDriver = providers.Factory(AddressMongodbDriver)
    address_manager: AddressManager = providers.Singleton(AddressManager, mongodb_driver=address_mongodb_driver)
    address_dto_handler: AddressDtoHandler = providers.Singleton(AddressDtoHandler)
    address_service: AddressService = providers.Singleton(
        AddressService,
        manager=address_manager,
        address_dto_handler=address_dto_handler,
        boundary_service=boundary.boundary_service,
        raw_address_service=location_raw.address_service,
        raw_point_geometry_service=location_raw.point_geometry_service,
        raw_continuous_geometry_service=location_raw.continuous_geometry_service
    )

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
        group_info_service=building_raw.group_info_service,
        title_info_service=building_raw.title_info_service
    )
