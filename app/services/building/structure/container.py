from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.building.structure.drivers.address.address_mongodb_driver import AddressMongodbDriver
from app.services.building.structure.handlers.address_dto_handler import AddressDtoHandler
from app.services.building.structure.managers.address_manager import AddressManager
from app.services.building.structure.services.address_service import AddressService
from app.services.location.raw.container import RawContainer
from app.services.location.boundary.container import BoundaryContainer


class StructureContainer(AbstractContainer):
    # 타 컨테이너 참조
    raw: RawContainer = providers.Container(RawContainer)
    boundary: BoundaryContainer = providers.Container(BoundaryContainer)

    address_mongodb_driver: AddressMongodbDriver = providers.Factory(AddressMongodbDriver)
    address_manager: AddressManager = providers.Factory(AddressManager, mongodb_driver=address_mongodb_driver)
    address_dto_handler: AddressDtoHandler = providers.Factory(AddressDtoHandler)
    address_service: AddressService = providers.Factory(
        AddressService,
        manager=address_manager,
        address_dto_handler=address_dto_handler,
        boundary_service=boundary.boundary_service,
        raw_address_service=raw.address_service,
        raw_point_geometry_service=raw.point_geometry_service,
        raw_continuous_geometry_service=raw.continuous_geometry_service
    )
