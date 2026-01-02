from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.adapters import HTTPAdapter
from requests_aws4auth import AWS4Auth
from boto3 import Session
from .abstract_driver import AbstractDriver

class CustomHttpConnection(RequestsHttpConnection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # HTTP, HTTPS 모두 동일한 maxsize 적용
        adapter = HTTPAdapter(pool_connections=300, pool_maxsize=300)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

class Opensearch(AbstractDriver):
    """
    OpenSearch 연결을 관리하는 클래스입니다.
    OpenSearch 클라이언트 생성 및 연결 객체 반환 기능을 제공합니다.
    """

    client: OpenSearch = None  # OpenSearch 클라이언트 객체를 저장하는 변수입니다.
    default_index: str = None  # 기본 인덱스 이름을 저장하는 변수입니다.

    def set_connection(self, conn: dict) -> 'Opensearch':
        """
        OpenSearch 연결을 설정합니다.

        Args:
            conn (dict): OpenSearch 연결 설정 정보가 포함된 객체.

        Returns:
            Opensearch: 설정된 OpenSearch 연결 객체 자신을 반환합니다.
        """
        self.default_index = conn.get('name', None)

        if conn.get('use_serverless', False):  # AWS Serverless 방식인지 확인
            self._set_serverless_connection(conn)
        else:
            self._set_standard_connection(conn)

        return self

    def _set_standard_connection(self, conn: dict):
        """
        일반 OpenSearch 연결 설정을 처리합니다.

        Args:
            conn (dict): OpenSearch 연결 설정 정보.
        """
        http_auth = (conn['user'], conn['password']) if conn['user'] and conn['password'] else None
        self.client = OpenSearch(
            hosts=[{
                'host': conn['host'],
                'port': conn['port']
            }],
            http_auth=(conn['user'], conn['password']),  # 사용자 인증
            use_ssl=conn.get('use_ssl', False),  # SSL 여부
            verify_certs=conn.get('verify_certs', False),  # 인증서 검증 여부
            ssl_assert_hostname=conn.get('ssl_assert_hostname', False),  # 호스트 이름 검증 여부
            ssl_show_warn=conn.get('ssl_show_warn', True),  # SSL 경고 표시 여부
            timeout=5,  # 타임아웃을 5초로
            max_retries=3,  # 최대 재시도 횟수를 3으로 설정
            retry_on_timeout=True,  # 타임아웃 시 재시도 활성화
            maxsize=100 # 최대 커넥션 수
        )

    def _set_serverless_connection(self, conn: dict):
        """
        AWS OpenSearch Serverless 연결 설정을 처리합니다.

        Args:
            conn (dict): OpenSearch 연결 설정 정보.
        """
        session = Session(
            aws_access_key_id=conn['aws']['access_key'],
            aws_secret_access_key=conn['aws']['secret_key'],
            region_name=conn['aws']['region'],

        )
        credentials = session.get_credentials()
        aws_auth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            conn['aws']['region'],
            "aoss",  # AWS OpenSearch Serverless 서비스 이름
            session_token=credentials.token
        )

        self.client = OpenSearch(
            hosts=[{
                'host': conn['host'],
                'port': conn['port']
            }],
            http_auth=aws_auth,
            use_ssl=conn.get('use_ssl', False),  # SSL 여부
            verify_certs=conn.get('verify_certs', False),  # 인증서 검증 여부
            ssl_assert_hostname=conn.get('ssl_assert_hostname', False),  # 호스트 이름 검증 여부
            ssl_show_warn=conn.get('ssl_show_warn', True),  # SSL 경고 표시 여부
            timeout=5,  # 타임아웃을 5초로
            max_retries=3,  # 최대 재시도 횟수를 3으로 설정
            retry_on_timeout=True,  # 타임아웃 시 재시도 활성화
            connection_class=CustomHttpConnection
        )


    def get_connection(self) -> OpenSearch:
        """
        OpenSearch 연결 객체를 반환합니다.

        Returns:
            OpenSearch: OpenSearch 연결 객체.

        Raises:
            ValueError: OpenSearch 연결이 설정되지 않은 경우 예외를 발생시킵니다.
        """
        if not self.client:
            self._raise_not_prepare_connection()
        return self.client

    def _raise_not_prepare_connection(self):
        """
        OpenSearch 연결이 설정되지 않은 경우 ValueError를 발생시킵니다.

        Raises:
            ValueError: OpenSearch 연결이 준비되지 않은 경우 예외를 발생시킵니다.
        """
        raise ValueError('OpenSearch 연결이 준비되지 않았습니다.')

# 외부로 노출할 클래스 목록
__all__ = ['Opensearch']