"""API 실행 진입점 모듈.

이 모듈은 FastAPI 기반 웹 애플리케이션의 실행을 담당합니다.
- DI(Dependency Injection) 컨테이너를 통해 필요한 서비스들을 주입받습니다
- Uvicorn ASGI 서버를 사용하여 FastAPI 애플리케이션을 실행합니다
- 개발 환경에서 hot reload 기능을 제공합니다
"""

import logging
from typing import Any, Dict, Union
from app.core.helpers.config import Config

import uvicorn

from app.core.runner import run_with_services
from app.core.logger import log_exception

def _get_uvicorn_config() -> Dict[str, Union[str, int, bool]]:
    """
    Uvicorn 서버 설정을 반환합니다.

    Returns:
        Dict[str, Union[str, int, bool]]: Uvicorn 설정 딕셔너리
            - app: FastAPI 앱 모듈 경로
            - host: 서버 호스트 주소
            - port: 서버 포트 번호
            - reload: 파일 변경 시 자동 재시작 여부
            - log_level: 로그 레벨
    """

    return {
        "app": "app.http.routes.route:route",  # FastAPI 앱 인스턴스 경로
        "host": "0.0.0.0",  # 모든 인터페이스에서 접근 허용
        "port": 8000,  # HTTP 포트
        "reload": True,  # 개발 모드: 파일 변경 시 자동 재시작
        "log_level": "info"  # 로그 레벨 설정
    }


def _start_uvicorn_server(config: Dict[str, Union[str, int, bool]],
        log_config: Any,
        logger: logging.Logger) -> None:
    """
    Uvicorn 서버를 시작합니다.

    Args:
        config (Dict[str, Union[str, int, bool]]): Uvicorn 서버 설정
        log_config (Any): 로그 설정 객체
        logger (logging.Logger): 로깅을 위한 Logger 객체

    Raises:
        Exception: 서버 실행 중 오류 발생 시
    """
    try:
        logger.info("🟢 Uvicorn 서버 실행 시작")
        logger.info(f"📍 서버 주소: http://{config['host']}:{config['port']}")
        logger.info(f"🔄 Hot Reload: {'활성화' if config['reload'] else '비활성화'}")

        # Uvicorn 서버 실행
        uvicorn.run(
            app=config["app"],
            host=config["host"],
            port=int(config["port"]),
            reload=bool(config["reload"]),
            log_level=str(config["log_level"]),
            log_config=log_config,
        )

        logger.info("✅ Uvicorn 서버 정상 종료")

    except Exception as e:
        logger.error(f"❌ Uvicorn 서버 실행 실패: {e}")
        raise


import logging
import traceback


def run_api(logger: logging.Logger, log_config: Any) -> None:
    try:
        uvicorn_config: Dict[str, Union[str, int, bool]] = _get_uvicorn_config()
        _start_uvicorn_server(uvicorn_config, log_config, logger)

    except Exception as e:
        # 현재 환경 확인
        env = Config.get('app.env', 'development')

        if env != 'production':
            # 개발/로컬 환경: 상세한 트레이스백 출력
            logger.error("❌ 상세 에러 스택트레이스 (Non-Production):", exc_info=True)
        else:
            # 운영 환경: 보안 및 로그 가독성을 위해 간략한 메시지만 출력
            logger.error(f"❌ 서버 실행 중 오류 발생 (Production): {e}")

        log_exception(logger, "Uvicorn 서버 실행", e)
        raise


def main() -> None:
    """
    애플리케이션 실행 진입점.

    DI 기반으로 logger와 관련 서비스들을 주입받아 run_api() 함수를 실행합니다.
    run_with_services는 애플리케이션의 부트스트랩 과정을 처리하고
    필요한 의존성들을 주입해줍니다.

    Note:
        bootstrap_condition=False로 설정하여 API 서버는 경량화된 부트스트랩을 수행합니다.
        이는 빠른 서버 시작을 위해 불필요한 초기화 과정을 생략합니다.
    """
    run_with_services(
        app_name="api",  # 애플리케이션 이름 (로깅 및 설정에 사용)
        main_fn=run_api,  # 실제 실행할 메인 함수
        bootstrap_condition=False  # 경량 부트스트랩 (API 서버용)
    )


# 스크립트가 직접 실행될 때만 main() 함수 호출
if __name__ == '__main__':
    main()
