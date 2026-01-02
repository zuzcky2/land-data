"""애플리케이션 최상위 DI 컨테이너 모듈.

전체 애플리케이션의 의존성 주입을 관리하는 루트 컨테이너입니다.
각 패키지별 컨테이너를 조합하여 애플리케이션 전체의 서비스를 제공합니다.
"""

from dependency_injector import containers, providers

from app.core.packages.support.container import Container as SupportContainer
from app.core.packages.database.container import Container as DatabaseContainer


class AppContainer(containers.DeclarativeContainer):
    """
    애플리케이션의 최상위 DI 컨테이너입니다.

    모든 패키지별 컨테이너를 조합하여 애플리케이션 전체의 의존성을 관리합니다.
    각 패키지 컨테이너는 독립적으로 구성되어 모듈성과 유지보수성을 보장합니다.

    Attributes:
        config (providers.Configuration): 전역 설정 프로바이더
        support (SupportContainer): 지원 서비스 컨테이너 (CLI, 스케줄러 등)
        database (DatabaseContainer): 데이터베이스 관련 서비스 컨테이너

    Note:
        wiring_config는 의도적으로 제거되었습니다.
        필요한 경우 수동으로 wire() 메서드를 호출하여 와이어링을 수행합니다.
    """

    # 전역 설정 프로바이더
    # 모든 하위 컨테이너에서 공유되는 설정을 제공합니다
    config = providers.Configuration()

    # 지원 서비스 컨테이너 (Support Package)
    # CLI 명령어 처리, 스케줄링, 로깅 등의 지원 기능을 제공합니다
    support: SupportContainer = providers.Container(
        SupportContainer,
        config=config.support  # support 설정 섹션을 하위 컨테이너에 주입
    )

    # 데이터베이스 서비스 컨테이너 (Database Package)
    # 데이터베이스 연결, ORM, 쿼리 관리 등의 데이터 접근 기능을 제공합니다
    database: DatabaseContainer = providers.Container(
        DatabaseContainer,
        config=config.database  # database 설정 섹션을 하위 컨테이너에 주입
    )

    # 향후 추가될 수 있는 다른 패키지 컨테이너들:
    # - auth: 인증/인가 관련 서비스
    # - notification: 알림 서비스
    # - storage: 파일 저장 서비스
    # - external: 외부 API 연동 서비스


__all__ = ['AppContainer']
