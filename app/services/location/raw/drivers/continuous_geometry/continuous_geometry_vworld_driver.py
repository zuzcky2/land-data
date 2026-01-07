from typing import List, Any
from app.services.location.raw.drivers.abstract_vworld_driver import AbstractVworldDriver
from app.services.location.raw.drivers.driver_interface import DriverInterface


class ContinuousGeometryVworldDriver(AbstractVworldDriver, DriverInterface):

    @property
    def call_config(self) -> dict:
        return {
            'api_path': '/req/data',
            'feature_data': 'LP_PA_CBND_BUBUN',
            'request': 'GetFeature',
            'service': 'data'
        }

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        params = {
            'geomFilter': f"POINT({self.arguments('latitude')} {self.arguments('longitude')})"
        }
        if single:
            self.set_pagination(page=1, per_page=1)

        # _call_api 내부에서 재시도 로직이 동작함
        res = self._call_api(params)
        self._last_raw_response = res

        try:
            items_container = res.get('response', {}).get('result', {}).get('featureCollection')
            if not items_container or not items_container.get('features'):
                return []

            items = items_container['features']
            return items if isinstance(items, list) else [items]
        except Exception:
            return []

    def _get_total_count(self) -> int:
        try:
            if not self._last_raw_response:
                return 0
            body = self._last_raw_response.get('response', {}).get('record', {})
            total_count = body.get('total', 0)
            return int(total_count)
        except (KeyError, TypeError, ValueError):
            return 0