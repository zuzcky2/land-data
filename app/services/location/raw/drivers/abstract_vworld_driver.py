from app.services.contracts.drivers.abstract import AbstractDriver
from abc import abstractmethod
from app.core.helpers.config import Config
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import requests
from typing import List


class AbstractVworldDriver(AbstractDriver):
    @property
    @abstractmethod
    def call_config(self) -> dict:
        return {}

    @property
    def config(self) -> dict:
        return {
            'host': Config.get('vworld.host'),
            'key': Config.get('vworld.key'),
            'domain': Config.get('vworld.domain'),
            'format': Config.get('vworld.format'),
            'crs': Config.get('vworld.crs')
        }

    def _call_api(self, params: dict) -> dict:
        """Vworld API 공통 호출 메서드 (Retry 및 Timeout 적용)"""

        url = f"{self.config['host']}{self.call_config.get('api_path')}"

        # 공통 파라미터 설정
        default_params = {
            'key': Config.get('vworld.key'),
            'domain': Config.get('vworld.domain'),
            'format': 'json',
            'crs': 'EPSG:4326',
            'service': self.call_config.get('service'),
            'version': '2.0',
            'request': self.call_config.get('request'),
            'data': self.call_config.get('feature_data'),
            'page': str(self.page),
            'size': str(self.per_page),
        }
        request_params = {**default_params, **params}

        # 재시도 전략 설정
        # total: 최대 재시도 횟수
        # backoff_factor: 재시도 간격 제어. 2 설정 시 (2, 4, 8초...) 순차 대기
        # status_forcelist: 재시도할 HTTP 상태 코드 (502 포함)
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # 1초 기준이며, 2회차부터 대기 시간이 늘어납니다.
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            try:
                # timeout 10초 적용
                response = session.get(url, params=request_params, timeout=10)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                # 재시도 끝에 실패하거나 기타 네트워크 에러 발생 시 로그 출력 후 예외 전파
                print(f"📡 API 호출 실패: {url} | Params: {params} | Error: {e}")
                raise e

    def store(self, items: List[dict]):
        raise NotImplementedError("주소검색 API 드라이버는 저장 기능을 지원하지 않습니다.")

