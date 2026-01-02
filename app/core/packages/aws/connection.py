from typing import Union
import boto3

class Connection:

    client: Union[boto3.Session, boto3.client]

    def set_connection(self, conn: dict, service_name: str) -> 'Connection':

        self.client = boto3.client(
            service_name,
            aws_access_key_id=conn['app_id'],
            aws_secret_access_key=conn['access_key'],
            region_name=conn['region']
        )

        return self

    def get_connection(self) -> boto3.client:
        if self.client:
            return self.client

        self._raise_not_prepare_connection()

    def _raise_not_prepare_connection(self):
        """
        연결이 준비되지 않았을 때 ValueError를 발생시킵니다.

        Raises:
            ValueError: 연결이 준비되지 않은 경우 예외를 발생시킵니다.
        """
        raise ValueError('AWS 연결이 준비되지 않았습니다.')

