"""지원 모듈(Support Layer) 의존성 주입 컨테이너.

- 환경변수, 설정(Config), 시간(KST), 로깅, 커맨드, 스케줄러 등
- 유틸리티 성격의 싱글톤 객체들을 제공
"""

from .abstracts.abstract_container import AbstractContainer, providers
from .modules.command import Command
from .modules.queue import Queue
from .modules.scheduler import Scheduler
from app.core.packages.database.container import Container as DatabaseContainer
from app.core.helpers.config import Config


class Container(AbstractContainer):
    """
    애플리케이션 지원 모듈을 관리하는 DI 컨테이너.

    - 주요 유틸 클래스들을 싱글톤으로 제공
    - 공통 기능들을 중앙 집중적으로 관리
    """
    database_container: DatabaseContainer = providers.Container(DatabaseContainer)

    command: providers.Singleton[Command] = providers.Singleton(
        Command
    )

    scheduler: providers.Singleton[Scheduler] = providers.Singleton(
        Scheduler, database_manager=database_container.manager
    )

    # ...
    # Redis 설정을 가져와서 Queue 모듈에 주입
    queue: providers.Singleton[Queue] = providers.Singleton(
        Queue,
        broker_url=f"redis://{Config.get('database.redis.host')}:{Config.get('database.redis.port')}/0",
        # 🚀 URI를 여기서 만들지 말고 설정 딕셔너리를 통째로 넘깁니다.
        mongo_cfg=Config.get('database.mongodb')
    )

# 외부에서 import 가능하도록 정의
__all__ = ["Container"]
