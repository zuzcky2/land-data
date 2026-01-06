"""
주소 JUSO_GO_KR
"""

from app.core.helpers.env import Env

# 주소 API 설정 구성
configs: dict = {
    # API 인증 키 (환경변수에서 로드, 필수값)
    'service_key': Env.get('JUSO_GO_KR_API_KEY', ''),

    'host': Env.get('JUSO_GO_KR_HOST', ''),
}

__all__ = ['configs']