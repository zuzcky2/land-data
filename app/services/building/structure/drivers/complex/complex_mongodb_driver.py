
from typing import Collection

from app.services.building.structure.drivers.abstract_mongodb_driver import AbstractMongodbDriver
from app.services.building.structure.drivers.driver_interface import DriverInterface
from app.facade import db

class ComplexMongodbDriver(AbstractMongodbDriver, DriverInterface):

    @property
    def primary_key(self) -> str:
        return 'building_manage_number'

    @property
    def collection(self) -> Collection:
        return db.get_mongodb_driver('mongodb') \
                            .get_database('landmark') \
                            .get_collection('complexes')

    @property
    def convert_types(self) -> dict:
        return {
            'building_manage_number': str
        }