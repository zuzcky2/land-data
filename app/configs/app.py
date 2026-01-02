"""애플리케이션 설정 관리 모듈.

애플리케이션의 기본 메타데이터와 파일 시스템 경로 설정을 관리합니다.
환경변수를 통해 설정값을 동적으로 로드하고, 기본값을 제공합니다.
"""

import os
from pathlib import Path
from app.core.helpers.env import Env


def _get_project_root() -> str:
    """프로젝트 루트 디렉토리 경로를 환경변수에서 로드하거나 현재 작업 디렉토리를 사용합니다."""
    project_root_raw: str = Env.get('PROJECT_ROOT', os.getcwd())
    return str(Path(project_root_raw).resolve())


def _get_storage_root(project_root: str) -> str:
    """스토리지 디렉토리 경로를 생성합니다. 상대 경로인 경우 프로젝트 루트 기준으로 절대 경로로 변환합니다."""
    storage_root_raw: str = Env.get('STORAGE_ROOT', f"{project_root}/storage")

    if not Path(storage_root_raw).is_absolute():
        storage_root_path: Path = Path(project_root) / storage_root_raw
    else:
        storage_root_path = Path(storage_root_raw)

    return str(storage_root_path.resolve())


# 프로젝트 루트 경로 먼저 확인 (다른 경로들의 기준이 됨)
project_root: str = _get_project_root()

# 애플리케이션 전역 설정 객체
configs: dict = {
    # 애플리케이션 메타데이터 설정
    'app_name': Env.get('APP_NAME', 'MyApp'),
    'app_version': Env.get('APP_VERSION', '1.0.0'),
    'env': Env.get('APP_ENV', 'local'),

    # 파일 시스템 경로 설정
    'project_root': project_root,
    'storage_root': _get_storage_root(project_root)
}

__all__ = ['configs']