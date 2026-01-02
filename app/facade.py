"""서비스 Facade 모듈.

애플리케이션의 주요 서비스들에 대한 간편한 접근을 제공하는 Facade 패턴 구현입니다.
DI 컨테이너를 통해 서비스 인스턴스를 가져와 전역적으로 사용할 수 있도록 합니다.
"""

from app.bootstrap import get_container
from typing import Tuple
from app.core.packages.support.modules.command import Command
from app.core.packages.support.modules.scheduler import Scheduler
from app.core.packages.database.manager import Manager


def _get_service_facade() -> Tuple[Command, Scheduler, Manager]:
    """
    DI 컨테이너에서 서비스 인스턴스들을 가져와 Facade 객체를 생성합니다.

    컨테이너가 초기화되지 않은 경우 자동으로 부트스트랩을 수행합니다.

    Returns:
        tuple: (command, scheduler, db) 서비스 인스턴스들의 튜플
    """
    try:
        container = get_container()
    except RuntimeError:
        # 컨테이너가 초기화되지 않은 경우 자동으로 부트스트랩 수행
        from app.bootstrap import bootstrap
        container = bootstrap()

    return (
        container.support.command(),  # CLI 명령어 처리 서비스
        container.support.scheduler(),  # 스케줄링 작업 관리 서비스
        container.database.manager()  # 데이터베이스 관리 서비스
    )


# 전역 서비스 인스턴스들
# 애플리케이션 어디서든 import하여 사용할 수 있습니다
command, scheduler, db = _get_service_facade()

# 서비스 인스턴스 설명:
# - command: CLI 명령어 실행, 메시지 출력, 로깅 등을 담당
# - scheduler: 백그라운드 작업 스케줄링 및 관리를 담당
# - db: 데이터베이스 연결, 쿼리 실행, 트랜잭션 관리를 담당

__all__ = ['command', 'db', 'scheduler']