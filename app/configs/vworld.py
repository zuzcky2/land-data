"""VWorld API 설정 관리 모듈.

VWorld (Virtual World) 공간정보 오픈플랫폼 API 연결 설정을 관리합니다.
지도, 지역경계, 주소검색 등의 공간정보 서비스 이용을 위한 설정을 제공합니다.
"""

from typing import Final
from app.core.helpers.env import Env


# 기본 설정 상수
DEFAULT_DATA_FORMAT: Final[str] = 'json'  # 기본 응답 데이터 형식
DEFAULT_CRS: Final[str] = 'EPSG:4326'  # 기본 좌표 참조 시스템 (WGS84 경위도)

# VWorld API 설정 구성
configs: dict = {
    # API 인증 키 (환경변수에서 로드, 필수값)
    'key': Env.get('V_WORLD_API_KEY', ''),

    # 허용 도메인 (환경변수에서 로드, 선택값)
    'domain': Env.get('V_WORLD_ALLOW_DOMAIN', ''),

    # 응답 데이터 형식 (JSON 고정, 파싱이 용이함)
    'format': DEFAULT_DATA_FORMAT,

    # 좌표 참조 시스템 (WGS84 경위도, GPS 표준 좌표계)
    'crs': DEFAULT_CRS
}

__all__ = ['configs']