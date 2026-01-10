from .abstract_slack_driver import AbstractSlackDriver
from ..driver_interface import DriverInterface

class DefaultSlackDriver(AbstractSlackDriver, DriverInterface):
    @property
    def channel(self) -> str:
        return 'default'