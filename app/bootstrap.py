"""애플리케이션 부트스트랩 모듈.

애플리케이션의 초기화와 DI 컨테이너 관리를 위한 편의 함수들을 제공합니다.
app/__init__.py의 ApplicationState를 래핑하여 더 간편한 API를 제공합니다.
"""

from typing import Optional, Dict, Any

from app import _app_state, AppContainer
from app.core.container import AppContainer


def bootstrap(config: Optional[Dict[str, Any]] = None) -> AppContainer:
    """
    애플리케이션을 초기화하고 DI 컨테이너를 반환합니다.

    애플리케이션의 모든 의존성을 설정하고 DI 컨테이너를 준비합니다.
    설정이 제공되지 않으면 app/configs에서 자동으로 로드됩니다.

    Args:
        config (Optional[Dict[str, Any]]): 컨테이너에 주입할 설정 딕셔너리.
                                            None인 경우 기본 설정을 사용합니다.

    Returns:
        AppContainer: 초기화된 DI 컨테이너 인스턴스

    Note:
        이 함수는 멀티스레드 환경에서 안전하며, 중복 호출 시 기존 컨테이너를 반환합니다.
    """
    return _app_state.initialize(config)


def get_container() -> AppContainer:
    """
    초기화된 DI 컨테이너 인스턴스를 반환합니다.

    애플리케이션의 모든 서비스와 의존성에 접근할 수 있는
    컨테이너 객체를 제공합니다.

    Returns:
        AppContainer: 초기화된 DI 컨테이너 인스턴스

    Raises:
        RuntimeError: 애플리케이션이 초기화되지 않은 경우
                        bootstrap() 함수를 먼저 호출해야 합니다.
    """
    return _app_state.get_container()


def is_initialized() -> bool:
    """
    애플리케이션의 초기화 상태를 확인합니다.

    Returns:
        bool: 애플리케이션이 초기화된 경우 True, 그렇지 않으면 False
    """
    return _app_state.is_initialized()


def reset_application() -> None:
    """
    애플리케이션 상태를 초기 상태로 리셋합니다.

    모든 DI 와이어링을 해제하고 컨테이너를 정리합니다.
    주로 테스트 환경에서 각 테스트 간 상태를 격리하기 위해 사용됩니다.

    Warning:
        이 함수를 호출하면 기존의 모든 의존성 주입이 무효화됩니다.
        운영 환경에서는 신중하게 사용해야 합니다.
    """
    _app_state.reset()


def get_app_state():
    """
    애플리케이션 상태 관리 객체를 반환합니다.

    고급 사용자나 특별한 상황에서 ApplicationState 객체에
    직접 접근해야 할 때 사용합니다.

    Returns:
        ApplicationState: 전역 애플리케이션 상태 인스턴스

    Note:
        일반적인 사용에서는 bootstrap(), get_container() 등의
        편의 함수를 사용하는 것을 권장합니다.
    """
    return _app_state


__all__ = [
    'bootstrap',
    'get_container',
    'is_initialized',
    'reset_application',
    'get_app_state'
]
