import pymongo
import urllib.parse
from .abstract_driver import AbstractDriver

class MongoDB(AbstractDriver):
    """
    MongoDB 연결을 관리하는 클래스입니다.
    MongoDB 클라이언트 생성 및 연결 객체 반환 기능을 제공합니다.
    """

    client: pymongo.MongoClient = None  # MongoDB 클라이언트 객체를 저장하는 변수입니다.
    default_database: str = None  # 기본 데이터베이스 이름을 저장하는 변수입니다.

    def set_connection(self, conn: dict) -> 'MongoDB':
        """
        MongoDB 연결을 설정합니다.

        Args:
            conn (dict): MongoDB 연결 설정 정보가 포함된 객체

        Returns:
            MongoDB: 설정된 MongoDB 연결 객체 자신을 반환합니다.
        """
        # 기본 데이터베이스 이름 설정
        self.default_database = conn['name']

        # MongoDB 클라이언트 생성
        # 사용자 이름과 비밀번호를 URL 인코딩하여 연결 문자열을 안전하게 구성합니다.


        self.client = pymongo.MongoClient(
            f"mongodb://{conn['user']}:{urllib.parse.quote(conn['password'])}"
            f"@{conn['host']}:{conn['port']}/{conn['name']}?"
            f"authMechanism=SCRAM-SHA-1&retryWrites=false&ssl=false"
        )

        return self

    def get_connection(self) -> pymongo.MongoClient:
        """
        MongoDB 연결 객체를 반환합니다.

        Returns:
            pymongo.MongoClient: MongoDB 연결 객체

        Raises:
            ValueError: MongoDB 연결이 설정되지 않은 경우 예외를 발생시킵니다.
        """
        # MongoDB 클라이언트가 설정되지 않았으면 예외를 발생시킵니다.
        if not self.client:
            self._raise_not_prepare_connection()
        return self.client

    def _raise_not_prepare_connection(self):
        """
        MongoDB 연결이 설정되지 않은 경우 ValueError를 발생시킵니다.

        Raises:
            ValueError: MongoDB 연결이 준비되지 않은 경우 예외를 발생시킵니다.
        """
        raise ValueError('MongoDB 연결이 준비되지 않았습니다.')

# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['MongoDB']