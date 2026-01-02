# app/services/building/raw/drivers/title_info/title_info_dgk.py

from typing import List, Any
from app.services.building.raw.drivers.abstract_dgk_driver import AbstractDgkDriver
from app.services.building.raw.drivers.driver_interface import \
    DriverInterface


class BasicInfoDgkDriver(AbstractDgkDriver, DriverInterface):

    @property
    def api_path(self) -> str:
        return '/1613000/BldRgstHubService/getBrBasisOulnInfo'
