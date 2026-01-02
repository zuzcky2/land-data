# app/services/building/raw/drivers/floor_info/floor_info_mongodb.py
from typing import Collection

from app.services.building.raw.drivers.abstract_mongodb_driver import AbstractMongodbDriver
from app.services.building.raw.drivers.driver_interface import DriverInterface
from app.facade import db

class FloorInfoMongodbDriver(AbstractMongodbDriver, DriverInterface):

    @property
    def primary_key(self) -> str:
        return 'mgmBldrgstPk'

    @property
    def collection(self) -> Collection:
        return db.get_mongodb_driver('mongodb') \
                            .get_database('landmark') \
                            .get_collection('building_raw_floor_info')

    @property
    def convert_types(self) -> dict:
        return {
            'mgmBldrgstPk': str
        }