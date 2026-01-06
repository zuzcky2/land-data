
from app.services.location.address.managers.search_manager import SearchManager
from app.services.location.address.managers.abstract_manager import AbstractManager
from app.services.location.address.services.abstract_service import AbstractService


class SearchService(AbstractService):

    def __init__(self, manager: SearchManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_address_search'

    @property
    def manager(self) -> AbstractManager:
        return self._manager

