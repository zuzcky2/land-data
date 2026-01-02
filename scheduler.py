"""스케줄러 실행 진입점 모듈.

백그라운드 작업 스케줄링을 담당하는 스케줄러 애플리케이션의 실행을 관리합니다.
- DI로 스케줄러 서비스를 주입받아 실행
- 로깅 및 예외 처리는 공통 유틸로 위임
- 애플리케이션 생명주기 관리
"""

import sys
from typing import Any
import logging

from app.core.runner import run_with_services
from app.core.logger import log_exception


def run_scheduler(logger: logging.Logger, log_config: Any) -> None:
    """
    스케줄러 애플리케이션 실행 함수.

    DI 컨테이너에서 스케줄러 서비스를 가져와서 백그라운드 작업을 시작합니다.
    스케줄러는 지속적으로 실행되며 등록된 작업들을 주기적으로 수행합니다.

    Args:
        logger (logging.Logger): 로깅을 위한 Logger 객체
        log_config (Any): 로그 설정 객체

    Raises:
        Exception: 스케줄러 실행 중 오류 발생 시
    """
    try:
        logger.info("🟢 스케줄러 애플리케이션 시작")

        # DI 컨테이너에서 스케줄러 서비스 가져오기
        from app.features.scheduler_kernel import scheduler

        # 스케줄러 실행 (블로킹 호출)
        logger.info("🔄 스케줄러 러너 시작")
        scheduler.runner.start()

        logger.info("✅ 스케줄러 정상 종료")

    except KeyboardInterrupt:
        # Ctrl+C로 종료한 경우
        logger.info("🛑 사용자에 의해 스케줄러가 중단되었습니다")

    except Exception as e:
        # 예외 발생 시 로그 기록 후 재발생
        log_exception(logger, "스케줄러 실행", e)
        sys.exit(1)


def main() -> None:
    """
    프로그램 실행 진입점.

    DI 기반으로 logger와 관련 서비스들을 주입받아 run_scheduler() 함수를 실행합니다.
    run_with_services는 애플리케이션의 부트스트랩 과정을 처리하고
    필요한 의존성들을 주입해줍니다.

    Note:
        bootstrap_condition=True로 설정하여 스케줄러는 모든 서비스가
        초기화된 후에 실행됩니다.
    """
    run_with_services(
        app_name='scheduler',  # 애플리케이션 이름 (로깅 및 설정에 사용)
        main_fn=run_scheduler,  # 실제 실행할 메인 함수
        bootstrap_condition=True  # 전체 부트스트랩 수행 (모든 서비스 필요)
    )


# 스크립트가 직접 실행될 때만 main() 함수 호출
if __name__ == '__main__':
    main()

__all__ = ['main', 'run_scheduler']
