from .abstract_connection import AbstractConnection
import boto3
from mypy_boto3_logs import CloudWatchLogsClient

class CloudwatchConnection(AbstractConnection):
    service_name: str = 'logs'
    client: CloudWatchLogsClient


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['CloudwatchConnection']

