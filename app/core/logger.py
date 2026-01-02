"""로깅 유틸리티 모듈.

애플리케이션의 로깅 설정과 예외 처리를 위한 유틸리티 함수들을 제공합니다.
- DI 기반으로 Logger 객체를 생성 및 설정
- 예외를 표준 형식으로 로깅하는 유틸 함수 제공
- 모듈별 로깅 설정을 동적으로 구성
"""

import traceback
import logging
import logging.config
from typing import Tuple, Dict, Any

from app.core.helpers.log import Log


def log_exception(logger: logging.Logger, context: str, error: Exception) -> None:
    """
    예외를 traceback과 함께 에러 로그로 출력합니다.

    발생한 예외의 전체 스택 트레이스를 포함하여 디버깅에 필요한
    모든 정보를 로그에 기록합니다.

    Args:
        logger (logging.Logger): 로그를 기록할 Logger 객체
        context (str): 예외 발생 위치 또는 작업 설명
                    예: "uvicorn 실행", "데이터베이스 연결", "API 요청 처리"
        error (Exception): 발생한 예외 객체
    """
    # 예외의 전체 스택 트레이스를 문자열로 변환
    tb: str = "".join(traceback.format_exception(
        type(error),
        error,
        error.__traceback__
    ))

    # 컨텍스트와 함께 에러 로그 기록
    logger.error(f"❌ {context} 중 예외 발생:\n{tb}")


def configure_logger(name: str) -> Tuple[logging.Logger, Dict[str, Any]]:
    """
    지정된 이름의 로거를 설정하고 Logger 객체와 설정을 반환합니다.

    Log 헬퍼 클래스를 통해 모듈별 로깅 설정을 가져와서
    Python 표준 logging 모듈에 적용합니다.

    Args:
        name (str): 로거 이름 및 식별자
                   사용 가능한 값: "command", "uvicorn", "api", "scheduler", "debug"

    Returns:
        Tuple[logging.Logger, Dict[str, Any]]:
            - logging.Logger: 설정이 적용된 Python 표준 Logger 객체
            - Dict[str, Any]: dictConfig용 로깅 설정 딕셔너리

    Raises:
        KeyError: 지정된 이름의 로거 설정이 존재하지 않는 경우
        Exception: 로깅 설정 적용에 실패한 경우

    Note:
        이 함수는 전역 로깅 설정을 변경하므로,
        애플리케이션 시작 시점에 한 번만 호출하는 것을 권장합니다.
    """
    try:
        # Log 헬퍼에서 로거와 설정 가져오기
        logger: logging.Logger = Log.get_logger(name)
        log_config: Dict[str, Any] = Log.get_config(name)

        # 로깅 설정을 시스템에 적용
        logging.config.dictConfig(log_config)

        return logger, log_config

    except KeyError as e:
        raise KeyError(f"로거 '{name}'의 설정을 찾을 수 없습니다: {e}")
    except Exception as e:
        raise Exception(f"로거 '{name}' 설정 중 오류 발생: {e}")


def get_logger(name: str) -> logging.Logger:
    """
    설정이 적용된 로거만 간단히 가져옵니다.

    configure_logger()의 편의 함수로, 설정 딕셔너리가 필요하지 않은 경우 사용합니다.

    Args:
        name (str): 로거 이름

    Returns:
        logging.Logger: 설정이 적용된 Logger 객체
    """
    logger, _ = configure_logger(name)
    return logger


__all__ = [
    'log_exception',
    'configure_logger',
    'get_logger'
]
