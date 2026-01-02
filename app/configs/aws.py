"""외부 서비스 연결 설정 관리 모듈.

AWS와 같은 클라우드 서비스와의 연결 설정을 관리합니다.
환경변수를 통해 민감한 인증 정보를 안전하게 로드합니다.
"""

from app.core.helpers.env import Env


# 애플리케이션 전역 설정 객체
configs: dict = {
    # 기본 드라이버로 landmark 설정
    'default_driver': 'landmark',

    # landmark 서비스 연결 설정 (AWS 연결 설정)
    'landmark': {
        'access_key': Env.get('AWS_ACCESS_KEY_ID', ''),
        'secret_key': Env.get('AWS_SECRET_ACCESS_KEY', ''),
        'region': Env.get('AWS_DEFAULT_REGION', 'ap-northeast-2')
    }
}

__all__ = ['configs']