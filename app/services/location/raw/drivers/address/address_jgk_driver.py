from typing import List, Any
from app.services.location.raw.drivers.abstract_jgk_driver import AbstractJgkDriver
from app.services.location.raw.drivers.driver_interface import DriverInterface


class AddressJgkDriver(AbstractJgkDriver, DriverInterface):

    @property
    def api_path(self) -> str:
        return '/addrlink/addrLinkApi.do'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        params = self.args or {}

        # 1. 검색 키워드 후보군 정리 (공백 제거 및 필터링)
        # 우선순위: road_address -> block_address

        if single:
            self.set_pagination(page=1, per_page=1)

        # 2. 순차적 검색 실행
        for keyword in params.get('search_queries'):
            # API 호출
            res = self._call_api({'keyword': keyword})
            self._last_raw_response = res

            try:
                results = res.get('results', {})
                common = results.get('common', {})
                items = results.get('juso')

                # 에러 체크 및 결과 유무 확인
                # errorCode가 '0'이 아니거나 juso가 None/빈 배열인 경우 실패로 간주
                if common.get('errorCode') == '0' and items:
                    return items if isinstance(items, list) else [items]

            except Exception as e:
                continue

        # 모든 키워드로 검색했으나 결과가 없는 경우
        return []

    def _get_total_count(self) -> int:
        try:
            if not self._last_raw_response:
                return 0
            body = self._last_raw_response.get('results', {}).get('common', {})
            total_count = body.get('totalCount', 0)
            return int(total_count)
        except (KeyError, TypeError, ValueError):
            return 0