"""데이터베이스 및 검색 엔진 연결 설정 관리 모듈.

MongoDB와 OpenSearch 연결 설정을 관리합니다.
환경변수를 통해 설정값을 동적으로 로드하고, 기본값을 제공합니다.
"""

from app.core.helpers.env import Env


def _get_boolean_env(env_key: str, default_value: bool) -> bool:
    """환경변수에서 불린 값을 안전하게 가져옵니다. true/1/yes/on은 True로 처리합니다."""
    env_value = Env.get(env_key, str(default_value))

    # None이나 비문자열 값 처리
    if env_value is None:
        return default_value

    # 문자열로 변환 후 소문자로 변환
    env_str = str(env_value).lower().strip()
    return env_str in ('true', '1', 'yes', 'on')


# 애플리케이션 전역 설정 객체
configs: dict = {
    # 기본 드라이버로 MongoDB 사용
    'default_driver': 'mongodb',

    # MongoDB 설정
    'mongodb': {
        'connection': 'mongodb',
        'host': Env.get('MONGO_HOST', 'localhost'),
        'port': Env.get('MONGO_PORT', '27017'),
        'name': Env.get('MONGO_NAME', ''),
        'user': Env.get('MONGO_USER', ''),
        'password': Env.get('MONGO_PASS', ''),
        'ssl': _get_boolean_env('MONGO_SSL', False)
    },

    # MySQL 설정
    'mysql': {
        'connection': 'mysql',
        'host': Env.get('MYSQL_HOST', 'localhost'),
        'port': Env.get('MYSQL_PORT', '3306'),
        'name': Env.get('MYSQL_NAME', ''),
        'user': Env.get('MYSQL_USER', 'root'),
        'password': Env.get('MYSQL_PASS', ''),
        'pool_recycle': 3600,
        'pool_pre_ping': True
    },
}

__all__ = ['configs']