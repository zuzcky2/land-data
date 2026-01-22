
from typing import Collection

from app.services.building.raw.drivers.abstract_mongodb_driver import AbstractMongodbDriver
from app.services.building.raw.drivers.driver_interface import DriverInterface
from app.facade import db

class KaptDetailMongodbDriver(AbstractMongodbDriver, DriverInterface):

    @property
    def primary_key(self) -> str:
        return 'kaptCode'

    @property
    def collection(self) -> Collection:
        return db.get_mongodb_driver('mongodb') \
                            .get_database('landmark') \
                            .get_collection('building_raw_kapt_detail')

    @property
    def convert_types(self) -> dict:
        return {
            'kaptCode': str
        }