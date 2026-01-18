from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.drivers.block_address.block_address_text_driver \
    import (BlockAddressTextDriver)
from app.services.location.raw.drivers.block_address.block_address_mongodb_driver \
    import (BlockAddressMongodbDriver)
from app.services.location.raw.drivers.driver_interface \
    import (DriverInterface)


class BlockAddressManager(AbstractManager):
    _text_driver: BlockAddressTextDriver
    _mongodb_driver: BlockAddressMongodbDriver

    def __init__(self, mongodb_driver: BlockAddressMongodbDriver, text_driver: BlockAddressTextDriver):
        self._mongodb_driver = mongodb_driver
        self._text_driver = text_driver

    @property
    def mongodb_driver(self) -> DriverInterface:
        return self._mongodb_driver

    @property
    def text_driver(self) -> DriverInterface:
        return self._text_driver

    def _create_text_driver(self) -> DriverInterface:
        return self.text_driver