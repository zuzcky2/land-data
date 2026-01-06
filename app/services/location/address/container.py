from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.location.address.drivers.search.search_jgk_driver import SearchJgkDriver
from app.services.location.address.drivers.search.search_mongodb_driver import SearchMongodbDriver
from app.services.location.address.managers.search_manager import SearchManager
from app.services.location.address.services.search_service import SearchService


class AddressContainer(AbstractContainer):
    search_jgk_driver: SearchJgkDriver = providers.Factory(SearchJgkDriver)
    search_mongodb_driver: SearchMongodbDriver = providers.Factory(SearchMongodbDriver)
    search_manager: SearchManager = providers.Singleton(
        SearchManager,
        jgk_driver=search_jgk_driver,
        mongodb_driver=search_mongodb_driver,
    )
    search_service: SearchService = providers.Singleton(SearchService, manager=search_manager)

