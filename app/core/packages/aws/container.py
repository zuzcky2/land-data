from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from .connections.cloudwatch_connection import CloudwatchConnection

class Container(AbstractContainer):

    cloudwatch_connection: CloudwatchConnection = providers.Singleton(CloudwatchConnection)

# 외부로 노출할 변수들을 지정합니다.
__all__ = ['Container']
