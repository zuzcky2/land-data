from app.services.building.raw.drivers.abstract_dgk_driver import AbstractDgkDriver
from app.services.building.raw.drivers.driver_interface import \
    DriverInterface
from typing import List

class KaptListDgkDriver(AbstractDgkDriver, DriverInterface):

    @property
    def api_path(self) -> str:
        return '/1613000/AptListService3/getTotalAptList3'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        params = self.args or {}

        if single:
            self.set_pagination(page=1, per_page=1)

        # _call_api 내부에서 재시도 로직이 동작함
        res = self._call_api(params)
        self._last_raw_response = res

        try:
            items_container = res.get('response', {}).get('body', {})
            if not items_container or not items_container.get('items'):
                return []

            items = items_container['items']

            return items if isinstance(items, list) else [items]
        except Exception:
            return []