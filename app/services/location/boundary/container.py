from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.location.boundary.drivers.mongodb import MongoDBDriver
from app.services.location.boundary.handlers.build_boundary_item_handler import BuildBoundaryItemHandler
from app.services.location.boundary.manager import BoundaryManager
from app.services.location.boundary.service import BoundaryService
from app.services.location.boundary.drivers.vworld import VWorldDriver


class BoundaryContainer(AbstractContainer):

    build_boundary_item_handler: BuildBoundaryItemHandler = providers.Singleton(BuildBoundaryItemHandler)

    mongodb_driver: MongoDBDriver = providers.Factory(MongoDBDriver)

    vworld_driver: VWorldDriver = providers.Factory(
        VWorldDriver,
        build_boundary_item_handler=build_boundary_item_handler
    )

    boundary_manager: BoundaryManager = providers.Singleton(
        BoundaryManager,
        mongodb_driver=mongodb_driver,
        vworld_driver=vworld_driver
    )

    boundary_service: BoundaryService = providers.Singleton(BoundaryService, boundary_manager=boundary_manager)