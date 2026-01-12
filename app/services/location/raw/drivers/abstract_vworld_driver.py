import json
import re
import requests
from abc import abstractmethod
from typing import List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.services.contracts.drivers.abstract import AbstractDriver
from app.core.helpers.config import Config


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
        """Vworld API 공통 호출 메서드 (JSON 이스케이프 문자 보정 및 Retry/Timeout 적용)"""

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

        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)

        with requests.Session() as session:
            session.mount("https://", adapter)
            session.mount("http://", adapter)

            try:
                response = session.get(url, params=request_params, timeout=10)
                response.raise_for_status()

                # 🚀 [수정 지점] JSON 파싱 에러 방지를 위한 보정 로직
                raw_text = response.text
                try:
                    # 일반적인 상황에서는 바로 파싱
                    return json.loads(raw_text)
                except json.JSONDecodeError:
                    # 이스케이프 에러 발생 시 (예: "시설-4\2") 
                    # 정상적인 이스케이프 패턴이 아닌 역슬래시(\)를 이중 역슬래시(\\)로 치환
                    fixed_text = re.sub(r'\\(?![/u"\\bdfnrt])', r'\\\\', raw_text)
                    return json.loads(fixed_text)

            except requests.exceptions.RequestException as e:
                print(f"📡 API 호출 실패: {url} | Params: {params} | Error: {e}")
                raise e
            except json.JSONDecodeError as e:
                print(f"❌ JSON 파싱 최종 실패: {url} | Error: {e}")
                raise e

    def store(self, items: List[dict]):
        raise NotImplementedError("주소검색 API 드라이버는 저장 기능을 지원하지 않습니다.")