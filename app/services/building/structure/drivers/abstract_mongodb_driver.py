from abc import abstractmethod, ABC

from app.services.contracts.drivers.abstract_mongodb_driver import AbstractMongodbDriver as AbstractDriver

class AbstractMongodbDriver(AbstractDriver, ABC):
    pass