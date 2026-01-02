import os
import importlib
from typing import Any, Dict
from .env import Env

class Config:
    """
    설정 값을 로드하고 관리하는 클래스입니다.

    Attributes:
        _CONFIG_MODULE_NAME (str): 설정 파일에서 참조할 최상위 변수명입니다.
        _relative_path (str): 설정 파일이 위치한 상대 경로입니다.
        _config_path (str): 설정 파일이 위치한 전체 경로입니다.
        env (Env): 환경 변수를 관리하는 Env 객체입니다.
        _cache (Dict[str, Any]): 설정 값을 캐싱하기 위한 딕셔너리입니다.
    """

    _CONFIG_MODULE_NAME = 'configs'  # 설정 파일 내 최상위 변수명
    _relative_path = 'app/configs'   # 설정 파일의 상대 경로

    _config_path = os.path.join(
        Env.get('PROJECT_ROOT', '/var/workspace/python'),
        _relative_path
    )  # 프로젝트 루트를 기준으로 설정 파일 경로를 구성합니다.
    _cache: Dict[str, Any] = {}  # 설정 값을 캐싱하기 위한 딕셔너리 초기화


    @staticmethod
    def get(config: str, default: Any = None) -> Any:
        """
        지정된 설정 값을 가져옵니다. 설정 파일이 없거나 값이 없으면 기본값을 반환합니다.
        설정 값을 가져올 때 캐싱된 데이터를 우선적으로 사용합니다.

        Args:
            config (str): 가져올 설정 값의 이름 (예: "database.host").
            default (Any, optional): 설정 값이 없을 경우 반환할 기본값입니다. 기본값은 None입니다.

        Returns:
            Any: 설정 값. 설정이 없으면 기본값을 반환합니다.
        """
        if config in Config._cache:
            return Config._cache[config]  # 캐시에 값이 있으면 반환

        configs = config.split('.')  # 설정 경로를 구분자로 나눠 리스트로 만듭니다.
        module_file = os.path.join(Config._config_path, f'{configs[0]}.py')  # 설정 파일 경로 구성

        # 설정 파일 경로나 디렉토리가 없으면 기본값을 반환
        if not os.path.exists(Config._config_path) or not os.path.exists(module_file):
            return default

        try:
            # 설정 파일을 동적으로 로드
            module_name = f"{Config._relative_path.replace('/', '.')}.{configs[0]}"
            module = importlib.import_module(module_name)
            config_data = getattr(module, Config._CONFIG_MODULE_NAME) #type ignore

            # 설정 값이 계층적 구조일 때 각 단계의 값에 접근
            for key in configs[1:]:
                config_data = config_data[key]


            Config._cache[config] = config_data  # 조회한 설정 값을 캐시에 저장
            return config_data
        except (AttributeError, KeyError, ImportError, TypeError):
            # 설정 값이 없거나 에러 발생 시 기본값을 반환
            return default

# 외부로 노출할 클래스 목록을 정의합니다.
__all__ = ['Config']