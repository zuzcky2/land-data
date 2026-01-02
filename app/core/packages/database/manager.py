"""데이터베이스 매니저 모듈.

다중 데이터베이스 드라이버를 통합 관리하는 매니저 클래스입니다.
- MongoDB, OpenSearch, MySQL 등 다양한 데이터베이스 지원
- 드라이버별 연결 설정 및 인스턴스 관리
- 설정 기반 동적 드라이버 선택
- 연결 상태 모니터링 및 헬스 체크
"""

from typing import Union, Optional, Dict, Any, List
import logging

from opensearchpy import OpenSearch
from pymongo import MongoClient

from app.core.packages.support.abstracts.abstract_manager import AbstractManager
from .drivers.opensearch import Opensearch
from .drivers.mongodb import MongoDB
from .drivers.mysql import MySQLDriver
from ...helpers.config import Config


class Manager(AbstractManager):
    """
    다중 데이터베이스 드라이버를 관리하는 매니저 클래스입니다.

    MongoDB, OpenSearch, MySQL 등 다양한 데이터베이스에 대한 통합된 인터페이스를 제공하며,
    설정 기반으로 드라이버를 동적으로 선택하고 연결을 관리합니다.

    Attributes:
        default_driver (str): 기본으로 사용할 데이터베이스 드라이버 이름
        _driver_cache (Dict): 드라이버 인스턴스 캐시 (성능 최적화용)
        _logger (logging.Logger): 매니저 전용 로거
    """

    def __init__(self) -> None:
        """
        데이터베이스 매니저를 초기화합니다.

        Args:
            config (Optional[Dict[str, Any]]): DI 컨테이너에서 주입받는 설정
                                                None인 경우 기본 설정을 사용합니다.
        """
        super().__init__()

        # 설정 로드 (DI 주입 설정 우선, 없으면 기본 설정 사용)
        self._config = Config.get('database')
        self.default_driver: str = self._config['default_driver']

        # 드라이버 인스턴스 캐시 (재사용을 위한 성능 최적화)
        self._driver_cache: Dict[str, Union[OpenSearch, MongoClient, MySQLDriver]] = {}

        # 매니저 전용 로거
        self._logger: logging.Logger = logging.getLogger('database.manager')

        self._logger.info(f"데이터베이스 매니저 초기화 완료 (기본 드라이버: {self.default_driver})")

    def get_mongodb_driver(
            self,
            driver_name: str,
            conn: Optional[dict] = None,
            use_cache: bool = True
    ) -> MongoClient:
        """
        MongoDB 드라이버 인스턴스를 반환합니다.

        Args:
            driver_name (str): 드라이버 식별자
            conn (Optional[MongoDBConfig]): MongoDB 연결 설정.
                                            None인 경우 설정에서 자동 로드
            use_cache (bool): 캐시된 인스턴스 사용 여부

        Returns:
            MongoClient: MongoDB 클라이언트 인스턴스

        Raises:
            ValueError: 드라이버 설정을 찾을 수 없는 경우
            ConnectionError: MongoDB 연결에 실패한 경우
        """
        cache_key = f"mongodb_{driver_name}"

        # 캐시된 인스턴스가 있고 캐시 사용이 활성화된 경우
        if use_cache and cache_key in self._driver_cache:
            self._logger.debug(f"MongoDB 드라이버 캐시 사용: {driver_name}")
            return self._driver_cache[cache_key]

        try:
            # 연결 설정 로드
            connection_config = conn or self.get_config(driver_name, 'mongodb')

            # MongoDB 드라이버 인스턴스 생성
            mongodb_driver = MongoDB()
            client = mongodb_driver.set_connection(connection_config).get_connection()

            # 캐시에 저장
            if use_cache:
                self._driver_cache[cache_key] = client

            self._logger.info(f"MongoDB 드라이버 생성 완료: {driver_name}")
            return client

        except Exception as e:
            self._logger.error(f"MongoDB 드라이버 생성 실패: {driver_name} - {e}")
            raise ConnectionError(f"MongoDB 연결 실패 ({driver_name}): {e}")

    def get_opensearch_driver(
            self,
            driver_name: str,
            conn: Optional[dict] = None,
            use_cache: bool = True
    ) -> OpenSearch:
        """
        OpenSearch 드라이버 인스턴스를 반환합니다.

        Args:
            driver_name (str): 드라이버 식별자
            conn (Optional[dict]): OpenSearch 연결 설정.
                                                None인 경우 설정에서 자동 로드
            use_cache (bool): 캐시된 인스턴스 사용 여부

        Returns:
            OpenSearch: OpenSearch 클라이언트 인스턴스

        Raises:
            ValueError: 드라이버 설정을 찾을 수 없는 경우
            ConnectionError: OpenSearch 연결에 실패한 경우
        """
        cache_key = f"opensearch_{driver_name}"

        # 캐시된 인스턴스가 있고 캐시 사용이 활성화된 경우
        if use_cache and cache_key in self._driver_cache:
            self._logger.debug(f"OpenSearch 드라이버 캐시 사용: {driver_name}")
            return self._driver_cache[cache_key]

        try:
            # 연결 설정 로드
            connection_config = conn or self.get_config(driver_name, 'opensearch')

            # OpenSearch 드라이버 인스턴스 생성
            opensearch_driver = Opensearch()
            client = opensearch_driver.set_connection(connection_config).get_connection()

            # 캐시에 저장
            if use_cache:
                self._driver_cache[cache_key] = client

            self._logger.info(f"OpenSearch 드라이버 생성 완료: {driver_name}")
            return client

        except Exception as e:
            self._logger.error(f"OpenSearch 드라이버 생성 실패: {driver_name} - {e}")
            raise ConnectionError(f"OpenSearch 연결 실패 ({driver_name}): {e}")

    def get_mysql_driver(
            self,
            driver_name: str,
            conn: Optional[dict] = None,
            use_cache: bool = True
    ) -> MySQLDriver:
        """
        MySQL 드라이버 인스턴스를 반환합니다.

        mysql-connector-python의 연결 풀을 사용하는 드라이버를 반환합니다.
        연결 풀이 자동으로 관리되므로 매번 새로운 연결을 가져올 필요가 없습니다.

        Args:
            driver_name (str): 드라이버 식별자
            conn (Optional[MySQLConfig]): MySQL 연결 설정.
                                            None인 경우 설정에서 자동 로드
            use_cache (bool): 캐시된 인스턴스 사용 여부

        Returns:
            MySQLDriver: MySQL 드라이버 인스턴스 (연결 풀 포함)

        Raises:
            ValueError: 드라이버 설정을 찾을 수 없는 경우
            ConnectionError: MySQL 연결에 실패한 경우

        Note:
            - 반환되는 MySQLDriver는 연결 풀을 포함
            - get_connection() 호출 시마다 풀에서 연결을 가져옴
            - 연결 사용 후 자동으로 풀에 반환됨
        """
        cache_key = f"mysql_{driver_name}"

        # 캐시된 인스턴스가 있고 캐시 사용이 활성화된 경우
        if use_cache and cache_key in self._driver_cache:
            self._logger.debug(f"MySQL 드라이버 캐시 사용: {driver_name}")
            return self._driver_cache[cache_key]

        try:
            # 연결 설정 로드
            connection_config = conn or self.get_config(driver_name, 'mysql')

            # MySQL 드라이버 인스턴스 생성 (연결 풀 포함)
            mysql_driver = MySQLDriver()
            mysql_driver.set_connection(connection_config)

            # 캐시에 저장
            if use_cache:
                self._driver_cache[cache_key] = mysql_driver

            self._logger.info(f"MySQL 드라이버 생성 완료: {driver_name}")
            return mysql_driver

        except Exception as e:
            self._logger.error(f"MySQL 드라이버 생성 실패: {driver_name} - {e}")
            raise ConnectionError(f"MySQL 연결 실패 ({driver_name}): {e}")

    def get_config(
            self,
            driver_name: str,
            connection_type: Optional[str] = None
    ) -> dict:
        """
        드라이버 이름에 해당하는 연결 설정을 반환합니다.

        Args:
            driver_name (str): 데이터베이스 드라이버 이름
            connection_type (Optional[str]): 예상되는 연결 타입 ('mongodb', 'opensearch', 'mysql')

        Returns:
            dict: 데이터베이스 연결 설정 객체

        Raises:
            ValueError: 드라이버 설정을 찾을 수 없거나 연결 타입이 일치하지 않는 경우
        """
        if driver_name not in self._config:
            self._raise_driver_not_found(driver_name)

        connection_config = self._config[driver_name]

        # 연결 타입 검증 (선택적)
        if connection_type and connection_config.get('connection') != connection_type:
            raise ValueError(
                f"드라이버 '{driver_name}'의 연결 타입이 '{connection_type}'과 일치하지 않습니다. "
                f"실제 타입: {connection_config.get('connection')}"
            )

        return connection_config

    def get_driver(
            self,
            driver_name: Optional[str] = None,
            use_cache: bool = True
    ) -> Union[OpenSearch, MongoClient, MySQLDriver]:
        """
        지정된 드라이버 이름에 해당하는 데이터베이스 드라이버 인스턴스를 반환합니다.

        Args:
            driver_name (Optional[str]): 데이터베이스 드라이버 이름.
                                        None인 경우 기본 드라이버를 사용합니다.
            use_cache (bool): 캐시된 인스턴스 사용 여부

        Returns:
            Union[OpenSearch, MongoClient, MySQLDriver]: 데이터베이스 드라이버 인스턴스

        Raises:
            ValueError: 드라이버를 찾을 수 없거나 지원하지 않는 타입인 경우
        """
        driver_name = driver_name or self.default_driver
        connection_config = self.get_config(driver_name)

        connection_type = connection_config.get('connection')

        if connection_type == 'opensearch':
            return self.get_opensearch_driver(driver_name, connection_config, use_cache)
        elif connection_type == 'mongodb':
            return self.get_mongodb_driver(driver_name, connection_config, use_cache)
        elif connection_type == 'mysql':
            return self.get_mysql_driver(driver_name, connection_config, use_cache)
        else:
            raise ValueError(f"지원하지 않는 데이터베이스 타입: {connection_type}")

    def get_available_drivers(self) -> List[str]:
        """
        사용 가능한 모든 드라이버 이름을 반환합니다.

        Returns:
            List[str]: 설정된 드라이버 이름 목록
        """
        return [key for key in self._config.keys() if key != 'default_driver']

    def health_check(self) -> Dict[str, Any]:
        """
        모든 설정된 데이터베이스의 연결 상태를 확인합니다.

        Returns:
            Dict[str, Any]: 각 드라이버별 연결 상태 정보
        """
        health_status = {}

        for driver_name in self.get_available_drivers():
            try:
                # 드라이버 인스턴스 생성 시도 (연결 테스트)
                driver = self.get_driver(driver_name, use_cache=False)

                # 드라이버별 헬스 체크 수행
                if isinstance(driver, MongoClient):
                    # MongoDB 헬스 체크
                    driver.admin.command('ping')
                    health_status[driver_name] = {
                        "status": "healthy",
                        "type": "mongodb",
                        "message": "연결 정상"
                    }
                elif isinstance(driver, OpenSearch):
                    # OpenSearch 헬스 체크
                    info = driver.info()
                    health_status[driver_name] = {
                        "status": "healthy",
                        "type": "opensearch",
                        "version": info.get('version', {}).get('number', 'unknown'),
                        "message": "연결 정상"
                    }
                elif isinstance(driver, MySQLDriver):
                    # MySQL 헬스 체크 (연결 풀에서 연결 가져와서 테스트)
                    connection = None
                    try:
                        connection = driver.get_connection()
                        cursor = connection.cursor()
                        cursor.execute("SELECT 1")
                        cursor.fetchone()
                        cursor.close()

                        health_status[driver_name] = {
                            "status": "healthy",
                            "type": "mysql",
                            "pool_size": driver.pool.pool_size if driver.pool else 0,
                            "message": "연결 정상"
                        }
                    finally:
                        if connection:
                            connection.close()  # 풀에 반환

            except Exception as e:
                health_status[driver_name] = {
                    "status": "unhealthy",
                    "message": f"연결 실패: {str(e)}"
                }

        return health_status

    def clear_cache(self, driver_name: Optional[str] = None) -> None:
        """
        드라이버 인스턴스 캐시를 정리합니다.

        Args:
            driver_name (Optional[str]): 정리할 특정 드라이버 이름.
                                        None인 경우 모든 캐시를 정리합니다.
        """
        if driver_name:
            # 특정 드라이버 캐시만 정리
            keys_to_remove = [key for key in self._driver_cache.keys()
                              if key.endswith(f"_{driver_name}")]
            for key in keys_to_remove:
                del self._driver_cache[key]
            self._logger.info(f"드라이버 캐시 정리 완료: {driver_name}")
        else:
            # 모든 캐시 정리
            self._driver_cache.clear()
            self._logger.info("모든 드라이버 캐시 정리 완료")

    def close_all_connections(self) -> None:
        """
        모든 활성 데이터베이스 연결을 정리합니다.

        애플리케이션 종료 시나 테스트 후 정리 작업에서 사용됩니다.
        """
        for cache_key, driver in self._driver_cache.items():
            try:
                if isinstance(driver, MongoClient):
                    driver.close()
                elif isinstance(driver, MySQLDriver):
                    # MySQL 드라이버의 연결 풀 종료
                    driver.close_pool()
                # OpenSearch는 별도 close 메서드가 없음
                self._logger.debug(f"연결 정리 완료: {cache_key}")
            except Exception as e:
                self._logger.warning(f"연결 정리 실패: {cache_key} - {e}")

        self.clear_cache()

    def _raise_driver_not_found(self, driver_name: str) -> None:
        """
        드라이버를 찾을 수 없는 경우 예외를 발생시킵니다.

        Args:
            driver_name (str): 찾을 수 없는 드라이버 이름

        Raises:
            ValueError: 드라이버 설정을 찾을 수 없음을 나타내는 예외
        """
        available_drivers = self.get_available_drivers()
        raise ValueError(
            f"드라이버 '{driver_name}'의 설정을 찾을 수 없습니다. "
            f"사용 가능한 드라이버: {available_drivers}"
        )


__all__ = ['Manager']