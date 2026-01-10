from .abstract_slack_driver import AbstractSlackDriver
from ..driver_interface import DriverInterface


class CommandSlackDriver(AbstractSlackDriver, DriverInterface):
    @property
    def channel(self) -> str:
        return 'command'