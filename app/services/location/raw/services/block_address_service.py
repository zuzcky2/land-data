from app.services.location.raw.managers.block_address_manager import BlockAddressManager
from app.services.location.raw.services.abstract_address_service import AbstractAddressService

class BlockAddressService(AbstractAddressService):
    def __init__(self, manager: BlockAddressManager):
        self._manager = manager

    @property
    def logger_name(self) -> str:
        return 'location_raw_block_address'

    @property
    def manager(self) -> BlockAddressManager:
        return self._manager