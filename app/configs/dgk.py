"""
공공데이터 DATA_GO_KR
"""

from app.core.helpers.env import Env

# VWorld API 설정 구성
configs: dict = {
    # API 인증 키 (환경변수에서 로드, 필수값)
    'service_key': Env.get('DATA_GO_KR_API_KEY', ''),

    'host': Env.get('DATA_GO_KR_HOST', ''),
}

__all__ = ['configs']