"""로깅 설정 관리 모듈.

애플리케이션의 각 모듈별 로깅 설정을 관리합니다.
환경변수를 통해 로그 레벨과 파일 경로를 동적으로 설정할 수 있습니다.
"""

from typing import Final
from app.core.helpers.env import Env


# 공통 로그 형식 설정 상수
DEFAULT_LOG_FORMAT: Final[str] = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 기본 로그 레벨 (환경변수로 전역 설정 가능)
DEFAULT_LOG_LEVEL: Final[str] = Env.get('DEFAULT_LOG_LEVEL', 'INFO')

# 로그 파일 모드 (환경변수로 설정 가능: 'w' 덮어쓰기, 'a' 추가)
DEFAULT_FILE_MODE: Final[str] = Env.get('LOG_FILE_MODE', 'w')


def _create_logging_config(
        module_name: str,
        default_filename: str,
        custom_level: str = None
) -> dict:
    """
    모듈별 로깅 설정을 생성합니다.

    Args:
        module_name (str): 모듈 이름 (환경변수 prefix로 사용)
        default_filename (str): 기본 로그 파일명
        custom_level (str, optional): 커스텀 로그 레벨

    Returns:
        LoggingConfig: 모듈별 로깅 설정
    """
    env_prefix = module_name.upper()

    return {
        'filename': Env.get(f'{env_prefix}_LOG_FILE', default_filename),
        'filemode': Env.get(f'{env_prefix}_LOG_MODE', DEFAULT_FILE_MODE),
        'format': Env.get(f'{env_prefix}_LOG_FORMAT', DEFAULT_LOG_FORMAT),
        'level': Env.get(f'{env_prefix}_LOG_LEVEL', custom_level or DEFAULT_LOG_LEVEL)
    }


# 각 모듈별 로깅 설정 구성
configs: dict = {
    # 디버그 로깅 설정 (개발 환경용)
    'debug': _create_logging_config('debug', 'debug.log'),

    # 스케줄러 로깅 설정 (백그라운드 작업용)
    'scheduler': _create_logging_config('scheduler', 'scheduler.log'),

    # 큐 로깅 설정 (백그라운드 작업용)
    'queue': _create_logging_config('queue', 'queue.log'),

    # 커맨드 로깅 설정 (CLI 실행용)
    'command': _create_logging_config('command', 'command.log'),

    # Uvicorn 웹서버 로깅 설정
    'uvicorn': _create_logging_config('uvicorn', 'uvicorn.log'),

    # API 로깅 설정 (요청/응답 추적용)
    'api': _create_logging_config('api', 'api.log'),

    'mongodb': _create_logging_config('mongodb', 'mongodb.log'),

    'slack': _create_logging_config('slack', 'slack.log'),

    'building_raw': _create_logging_config('building_raw', 'building_raw.log'),
    'building_raw_group_info': _create_logging_config('building_raw_group_info', 'building_raw/building_raw_group_info.log'),
    'building_raw_title_info': _create_logging_config('building_raw_title_info', 'building_raw/building_raw_title_info.log'),
    'building_raw_basic_info': _create_logging_config('building_raw_basic_info', 'building_raw/building_raw_basic_info.log'),
    'building_raw_floor_info': _create_logging_config('building_raw_floor_info', 'building_raw/building_raw_floor_info.log'),
    'building_raw_area_info': _create_logging_config('building_raw_area_info', 'building_raw/building_raw_area_info.log'),
    'building_raw_price_info': _create_logging_config('building_raw_price_info', 'building_raw/building_raw_price_info.log'),
    'building_raw_address_info': _create_logging_config('building_raw_address_info', 'building_raw/building_raw_address_info.log'),
    'building_raw_relation_info': _create_logging_config('building_raw_relation_info', 'building_raw/building_raw_relation_info.log'),
    'building_raw_zone_info': _create_logging_config('building_raw_zone_info', 'building_raw/building_raw_zone_info.log'),

    'location_raw_address_group': _create_logging_config('location_raw_address_group', 'location_raw/address_group.log'),
    'location_raw_address_title': _create_logging_config('location_raw_address_title', 'location_raw/address_title.log'),
    'building_structure_address_build': _create_logging_config('building_structure_address_build', 'building_structure/address_build.log'),
}

__all__ = ['configs']