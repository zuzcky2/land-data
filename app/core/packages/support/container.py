"""지원 모듈(Support Layer) 의존성 주입 컨테이너.

- 환경변수, 설정(Config), 시간(KST), 로깅, 커맨드, 스케줄러 등
- 유틸리티 성격의 싱글톤 객체들을 제공
"""

from .abstracts.abstract_container import AbstractContainer, providers
from .modules.command import Command
from .modules.scheduler import Scheduler


class Container(AbstractContainer):
    """
    애플리케이션 지원 모듈을 관리하는 DI 컨테이너.

    - 주요 유틸 클래스들을 싱글톤으로 제공
    - 공통 기능들을 중앙 집중적으로 관리
    """

    command: providers.Singleton[Command] = providers.Singleton(
        Command
    )
    """명령어 실행 핸들러 (환경, 시간, 로거 주입)"""

    scheduler: providers.Singleton[Scheduler] = providers.Singleton(
        Scheduler, command=command
    )
    """작업 스케줄링 핸들러 (command 의존)"""


# 외부에서 import 가능하도록 정의
__all__ = ["Container"]
