"""애플리케이션 실행 유틸리티 모듈.

애플리케이션의 생명주기를 관리하고 로깅, 부트스트랩, 정리 작업을 자동화합니다.
- 로깅 설정 자동 구성
- DI 컨테이너 부트스트랩 및 정리
- 예외 처리 및 로깅
- 애플리케이션별 실행 환경 제공
"""

import importlib
from typing import List, Optional, Callable, Any, Tuple
import logging

from app.core.logger import configure_logger, log_exception


def run_with_logging(app_name: str, main_fn: Callable[[logging.Logger, Any], None]) -> None:
    """
    로깅 설정과 함께 애플리케이션을 실행합니다.

    지정된 애플리케이션 이름으로 로거를 설정하고, 메인 함수를 실행합니다.
    예외 발생 시 적절한 로깅을 수행한 후 예외를 재발생시킵니다.

    Args:
        app_name (str): 애플리케이션 이름 (로거 식별자로 사용)
        main_fn (Callable[[logging.Logger, Any], None]):
            실행할 메인 함수. logger와 log_config를 매개변수로 받아야 합니다.

    Raises:
        Exception: 메인 함수 실행 중 발생한 모든 예외를 재발생
    """
    logger: Optional[logging.Logger] = None

    try:
        # 로거 설정 구성
        logger, log_config = configure_logger(app_name)
        logger.info(f"🚀 {app_name} 애플리케이션 시작")

        # 메인 함수 실행
        main_fn(logger, log_config)

    except Exception as e:
        # 예외 발생 시 로깅 처리
        try:
            # 로거가 이미 설정된 경우 재사용, 그렇지 않으면 새로 설정
            if logger is None:
                logger, _ = configure_logger(app_name)
            log_exception(logger, f"{app_name} 실행", e)
        except Exception:
            # 로깅도 실패한 경우 최후의 수단으로 콘솔 출력
            print(f"❌ '{app_name}' 실행 중 치명적 오류 발생")
            print(f"원본 오류: {e}")

        # 원본 예외를 재발생시켜 상위 레벨에서 처리할 수 있도록 함
        raise e


def run_with_services(
        app_name: str,
        main_fn: Callable[[logging.Logger, Any], None],
        bootstrap_condition: bool = True
) -> None:
    """
    서비스 부트스트랩과 함께 애플리케이션을 실행합니다.

    애플리케이션의 전체 생명주기를 관리합니다:
    1. 로깅 설정
    2. DI 컨테이너 부트스트랩 (선택적)
    3. 메인 함수 실행
    4. 리소스 정리

    Args:
        app_name (str): 애플리케이션 이름
        main_fn (Callable[[logging.Logger, Any], None]): 실행할 메인 함수
        bootstrap_condition (bool): 부트스트랩 수행 여부.
                                    True면 DI 컨테이너를 초기화하고,
                                    False면 경량 실행 모드를 사용합니다.

    Note:
        bootstrap_condition=False는 API 서버와 같이 빠른 시작이 필요한 경우에 유용합니다.
        bootstrap_condition=True는 CLI 명령어와 같이 모든 서비스가 필요한 경우에 사용합니다.
    """

    def wrapped_main_fn(logger: logging.Logger, log_config: Any) -> None:
        """
        메인 함수를 래핑하여 부트스트랩과 정리 작업을 수행합니다.

        Args:
            logger (logging.Logger): 설정된 로거 객체
            log_config (Any): 로그 설정 객체
        """
        try:
            # 부트스트랩 단계
            if bootstrap_condition:
                logger.info("🔄 애플리케이션 bootstrap 시작")

                # DI 컨테이너 초기화
                from app.bootstrap import bootstrap
                bootstrap()

                logger.info("✅ Bootstrap 완료")

            # 메인 함수 실행
            main_fn(logger, log_config)

        finally:
            # 정리 단계 (예외 발생 여부와 관계없이 실행)
            try:
                logger.info("🔄 애플리케이션 정리")

                # DI 컨테이너 정리
                from app.bootstrap import reset_application
                reset_application()

                logger.info("✅ 정리 완료")
            except Exception as cleanup_error:
                # 정리 작업 실패는 로그만 남기고 무시
                logger.warning(f"⚠️ 정리 작업 중 오류 발생: {cleanup_error}")

    # 로깅과 함께 래핑된 메인 함수 실행
    run_with_logging(app_name, wrapped_main_fn)


def run_with_bootstrap(
        app_name: str,
        main_fn: Callable[[logging.Logger, Any], None],
        **kwargs: Any
) -> None:
    """
    기존 호환성을 위한 함수입니다.

    run_with_services()의 별칭으로, 기존 코드와의 호환성을 유지합니다.
    새로운 코드에서는 run_with_services()를 직접 사용하는 것을 권장합니다.

    Args:
        app_name (str): 애플리케이션 이름
        main_fn (Callable[[logging.Logger, Any], None]): 실행할 메인 함수
        **kwargs: run_with_services()에 전달할 추가 인자들

    Deprecated:
        이 함수는 하위 호환성을 위해 유지되지만,
        새로운 코드에서는 run_with_services()를 사용하세요.
    """
    return run_with_services(app_name, main_fn, **kwargs)


__all__ = [
    'run_with_logging',
    'run_with_services',
    'run_with_bootstrap'  # 하위 호환성을 위해 유지
]
