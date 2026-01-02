"""서비스 캐시 관리 모듈.

서비스 인스턴스를 메모리에 캐시하여 중복 생성을 방지하고 성능을 향상시킵니다.
싱글톤 패턴과 유사하게 동작하여 동일한 서비스는 한 번만 생성됩니다.
"""

from typing import Dict, Any, Callable, TypeVar, Optional
import threading

# 서비스 타입을 위한 제네릭 타입 변수
ServiceType = TypeVar('ServiceType')

# 전역 서비스 캐시 저장소
# 키: 서비스 이름, 값: 서비스 인스턴스
_service_cache: Dict[str, Any] = {}

# 멀티스레드 환경에서 캐시 접근을 보호하기 위한 락
_cache_lock: threading.Lock = threading.Lock()


def get_service_with_cache(
        service_name: str,
        service_fn: Callable[[], ServiceType]
) -> ServiceType:
    """
    서비스 인스턴스를 캐시와 함께 가져옵니다.

    지정된 서비스가 캐시에 있으면 기존 인스턴스를 반환하고,
    없으면 서비스 생성 함수를 호출하여 새 인스턴스를 생성하고 캐시에 저장합니다.

    Args:
        service_name (str): 캐시에서 사용할 서비스 식별자
        service_fn (Callable[[], ServiceType]): 서비스 인스턴스를 생성하는 함수
                                                파라미터가 없고 서비스 인스턴스를 반환해야 합니다.

    Returns:
        ServiceType: 캐시된 또는 새로 생성된 서비스 인스턴스

    Note:
        이 함수는 멀티스레드 환경에서 안전하며, 동일한 서비스는 한 번만 생성됩니다.
    """
    with _cache_lock:
        # 캐시에 서비스가 있는지 확인
        if service_name in _service_cache:
            return _service_cache[service_name]

        # 캐시에 없는 경우 새 인스턴스 생성
        service_instance = service_fn()

        # 생성된 인스턴스를 캐시에 저장
        _service_cache[service_name] = service_instance

        return service_instance


def clear_service_cache(service_name: Optional[str] = None) -> None:
    """
    서비스 캐시를 지웁니다.

    Args:
        service_name (Optional[str]): 지울 서비스 이름.
                                        None인 경우 모든 캐시를 지웁니다.
    """
    with _cache_lock:
        if service_name is None:
            # 모든 캐시 제거
            _service_cache.clear()
        elif service_name in _service_cache:
            # 특정 서비스 캐시 제거
            del _service_cache[service_name]


def get_cached_services() -> Dict[str, Any]:
    """
    현재 캐시된 모든 서비스의 복사본을 반환합니다.

    Returns:
        Dict[str, Any]: 캐시된 서비스들의 딕셔너리 (읽기 전용 복사본)

    Note:
        반환된 딕셔너리는 복사본이므로 수정해도 실제 캐시에는 영향을 주지 않습니다.
    """
    with _cache_lock:
        return _service_cache.copy()


def is_service_cached(service_name: str) -> bool:
    """
    특정 서비스가 캐시되어 있는지 확인합니다.

    Args:
        service_name (str): 확인할 서비스 이름

    Returns:
        bool: 서비스가 캐시되어 있으면 True, 그렇지 않으면 False
    """
    with _cache_lock:
        return service_name in _service_cache


__all__ = [
    'get_service_with_cache',
    'clear_service_cache',
    'get_cached_services',
    'is_service_cached'
]
