
from typing import Collection

from app.services.location.raw.drivers.abstract_mongodb_driver import AbstractMongodbDriver
from app.services.location.raw.drivers.driver_interface import DriverInterface
from app.facade import db

class AddressMongodbDriver(AbstractMongodbDriver, DriverInterface):

    @property
    def primary_key(self) -> str:
        return 'bdMgtSn'

    @property
    def collection(self) -> Collection:
        return db.get_mongodb_driver('mongodb') \
                            .get_database('landmark') \
                            .get_collection('location_address_search')

    @property
    def convert_types(self) -> dict:
        return {
            'bdMgtSn': str
        }