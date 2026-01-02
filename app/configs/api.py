"""API 설정 관리 모듈.

FastAPI 애플리케이션의 전역 설정을 관리합니다.
환경변수를 통해 설정값을 동적으로 로드하고, 기본값을 제공합니다.
"""
from app.core.helpers.env import Env


# 애플리케이션 전역 설정 객체
configs: dict = {
    # 애플리케이션 경로 설정
    'root_path': Env.get('ROOT_PATH', ''),

    # API 문서 관련 URL 설정
    'openapi_url': Env.get('OPENAPI_URL', '/openapi.json'),
    'redoc_url': None,

    # 애플리케이션 메타데이터 설정
    'title': Env.get('APP_TITLE', 'search'),
    'description': Env.get('APP_DESCRIPTION', 'search description'),
    'version': Env.get('APP_VERSION', '1.0.0'),

    # 로깅 설정
    'log_level': Env.get('API_LOG_LEVEL', 'warning')
}

__all__ = ['configs']