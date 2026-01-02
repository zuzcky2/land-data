"""
MySQL 데이터베이스 드라이버 모듈

이 모듈은 AbstractDriver를 상속받아 MySQL 데이터베이스 연결을 관리하는 클래스를 제공합니다.
mysql-connector-python의 연결 풀을 사용하여 안정적이고 효율적인 연결 관리를 제공합니다.
"""

from mysql.connector import pooling
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from contextlib import contextmanager
import logging
from .abstract_driver import AbstractDriver

logger = logging.getLogger(__name__)


class MySQLDriver(AbstractDriver):
    """
    MySQL 연결 풀을 관리하는 클래스입니다.

    Oracle 공식 mysql-connector-python 라이브러리의 연결 풀을 사용하여
    효율적이고 안정적인 데이터베이스 연결을 제공합니다.

    Features:
        - 연결 풀을 통한 효율적인 연결 관리
        - 자동 재연결 및 연결 검증
        - 스레드 안전
        - 타임아웃 자동 처리

    Attributes:
        pool (MySQLConnectionPool): MySQL 연결 풀 객체
        default_database (str): 기본 데이터베이스 이름
    """

    pool: MySQLConnectionPool = None
    default_database: str = None

    def set_connection(self, conn: dict) -> 'MySQLDriver':
        """
        MySQL 연결 풀을 설정합니다.

        Args:
            conn (dict): MySQL 연결 설정 정보가 포함된 객체

        Returns:
            MySQLDriver: 설정된 MySQL 드라이버 객체 자신을 반환합니다.

        Note:
            - 연결 풀 크기는 pool_size로 제어 (기본 10개)
            - pool_reset_session=True로 연결 재사용 시 세션 초기화
            - autocommit=False로 명시적 트랜잭션 관리
        """
        self.default_database = conn['name']

        logger.info(f"MySQL 연결 풀 초기화 중: {conn['host']}:{conn['port']}/{conn['name']}")

        # 연결 풀 설정
        pool_config = {
            'pool_name': f"pool_{conn['name']}",
            'pool_size': 10,  # 연결 풀 크기
            'pool_reset_session': True,  # 세션 초기화
            'host': conn['host'],
            'port': conn['port'],
            'database': conn['name'],
            'user': conn['user'],
            'password': conn['password'],
            'charset': 'utf8mb4',
            'autocommit': False,
            'use_unicode': True,
            'get_warnings': True,
            'raise_on_warnings': False,
            'connection_timeout': 10,  # 연결 타임아웃 (초)
        }

        try:
            # 연결 풀 생성
            self.pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info(f"MySQL 연결 풀 초기화 완료 (풀 크기: {self.pool.pool_size})")
        except Exception as e:
            logger.error(f"MySQL 연결 풀 초기화 실패: {e}")
            raise

        return self

    def get_connection(self) -> PooledMySQLConnection:
        """
        연결 풀에서 MySQL 연결 객체를 가져옵니다.

        매번 호출 시 풀에서 유효한 연결을 가져오며,
        연결이 끊어진 경우 자동으로 재연결됩니다.

        Returns:
            PooledMySQLConnection: 풀에서 가져온 MySQL 연결 객체

        Raises:
            ValueError: 연결 풀이 설정되지 않은 경우 예외를 발생시킵니다.

        Note:
            - 연결 사용 후 반드시 close() 호출 필요 (풀에 반환)
            - with 문 사용 권장
            - 연결 유효성은 자동으로 검증됨
        """
        if not self.pool:
            logger.error("MySQL 연결 풀이 초기화되지 않음")
            self._raise_not_prepare_connection()

        try:
            # 연결 풀에서 연결 가져오기
            connection = self.pool.get_connection()

            # 연결 유효성 확인 (자동 재연결)
            if connection.is_connected():
                logger.debug("연결 풀에서 유효한 연결 획득")
            else:
                logger.warning("연결이 끊어져 재연결 시도")
                connection.reconnect(attempts=3, delay=1)

            return connection

        except Exception as e:
            logger.error(f"연결 풀에서 연결 획득 실패: {e}")
            raise

    @contextmanager
    def get_cursor(self, dictionary=True, buffered=True):
        """
        자동으로 닫히는 커서를 반환하는 context manager

        Args:
            dictionary (bool): True면 딕셔너리 형태로 결과 반환
            buffered (bool): True면 버퍼링된 커서 사용

        Yields:
            cursor: MySQL 커서 객체

        Note:
            - with 블록 종료 시 자동으로 커서와 연결이 닫힘
            - 연결은 풀에 반환됨

        Example:
            >>> with driver.get_cursor() as cursor:
            ...     cursor.execute("SELECT * FROM users")
            ...     results = cursor.fetchall()
        """
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
            yield cursor

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()  # 풀에 반환

    def execute(self, query: str, params: tuple = None, dictionary=True):
        """
        쿼리를 실행하고 결과를 반환합니다.

        Args:
            query (str): 실행할 SQL 쿼리
            params (tuple): 쿼리 파라미터
            dictionary (bool): 결과를 딕셔너리로 반환할지 여부

        Returns:
            list: 쿼리 결과 리스트

        Note:
            - 자동으로 커서와 연결을 관리
            - SELECT 쿼리에 적합
        """
        with self.get_cursor(dictionary=dictionary) as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_many(self, query: str, params_list: list):
        """
        여러 개의 쿼리를 일괄 실행합니다.

        Args:
            query (str): 실행할 SQL 쿼리
            params_list (list): 파라미터 리스트

        Note:
            - INSERT, UPDATE, DELETE에 적합
            - 자동 커밋은 하지 않으므로 필요시 명시적으로 commit 호출
        """
        connection = None
        cursor = None

        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            cursor.executemany(query, params_list)
            connection.commit()

        except Exception as e:
            if connection:
                connection.rollback()
            raise

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def close_pool(self):
        """
        연결 풀을 종료하고 모든 연결을 닫습니다.

        애플리케이션 종료 시 호출해야 합니다.

        Note:
            - 풀의 모든 연결을 정리
            - 일반적으로 애플리케이션 종료 시에만 호출
        """
        if self.pool:
            logger.info("MySQL 연결 풀 종료 중...")
            # mysql-connector-python은 명시적인 풀 종료 메서드가 없음
            # 가비지 컬렉션에 의해 자동 정리됨
            self.pool = None
            logger.info("MySQL 연결 풀 종료 완료")

    def _raise_not_prepare_connection(self):
        """
        MySQL 연결이 설정되지 않은 경우 ValueError를 발생시킵니다.

        Raises:
            ValueError: MySQL 연결 풀이 준비되지 않은 경우 예외를 발생시킵니다.
        """
        raise ValueError('MySQL 연결 풀이 준비되지 않았습니다.')


# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['MySQLDriver']