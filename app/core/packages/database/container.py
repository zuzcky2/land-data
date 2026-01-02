"""데이터베이스 패키지 DI 컨테이너 모듈.

데이터베이스 관련 서비스들의 의존성 주입을 관리하는 컨테이너입니다.
- 데이터베이스 매니저 및 드라이버 관리
- 연결 풀 및 설정 관리
- 싱글톤 패턴으로 리소스 효율성 보장
"""

from typing import Optional

from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from .manager import Manager


class Container(AbstractContainer):
    """
    데이터베이스 패키지의 의존성 주입을 관리하는 컨테이너 클래스입니다.

    데이터베이스 연결, 드라이버 관리, 쿼리 실행 등 데이터 접근 계층의
    모든 서비스를 중앙 집중적으로 관리합니다.

    Attributes:
        manager (providers.Singleton[Manager]): 데이터베이스 매니저 싱글톤 인스턴스
                                                다중 데이터베이스 드라이버를 관리합니다.

    Note:
        싱글톤 패턴을 사용하여 데이터베이스 연결과 리소스를 효율적으로 관리합니다.
        애플리케이션 전체에서 하나의 매니저 인스턴스를 공유합니다.
    """

    # 데이터베이스 매니저 싱글톤 인스턴스
    # MongoDB, OpenSearch 등 다중 데이터베이스 드라이버를 관리합니다
    manager: providers.Singleton[Manager] = providers.Singleton(
        Manager,
    )

    def __init__(self, config: Optional[providers.Configuration] = None) -> None:
        """
        데이터베이스 컨테이너를 초기화합니다.

        Args:
            config (Optional[providers.Configuration]): 상위 컨테이너에서 주입받는 설정
                                                        None인 경우 기본 설정을 사용합니다.
        """
        super().__init__()

        self._initialize_providers()

    def _initialize_providers(self) -> None:
        """
        데이터베이스 관련 프로바이더들을 초기화합니다.

        향후 추가적인 데이터베이스 서비스나 유틸리티가 필요한 경우
        이 메서드에서 초기화할 수 있습니다.

        Example:
            - 연결 풀 관리자
            - 캐시 매니저
            - 마이그레이션 도구
            - 백업 서비스
        """
        # 현재는 추가 초기화가 없으나, 향후 확장을 위한 메서드입니다
        # 예시:
        # self.connection_pool = providers.Singleton(ConnectionPool, config=self.config.pool)
        # self.cache_manager = providers.Singleton(CacheManager, config=self.config.cache)
        pass


__all__ = ['Container']
