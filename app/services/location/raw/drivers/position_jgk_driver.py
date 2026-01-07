

from typing import List, Any
from app.services.location.raw.drivers.abstract_jgk_driver import AbstractJgkDriver
from app.services.location.raw.drivers.driver_interface import DriverInterface


class PositionJgkDriver(AbstractJgkDriver, DriverInterface):

    @property
    def api_path(self) -> str:
        return '/addrlink/addrCoordApi.do'
