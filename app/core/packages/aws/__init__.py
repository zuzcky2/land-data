from dependency_injector.wiring import Provide, inject
from app.core.packages.aws.container import Container
from typing import Union
from .connections.cloudwatch_connection import CloudwatchConnection

@inject
def main(
    _cloudwatch_connection: Container.cloudwatch_connection = Provide[Container.cloudwatch_connection],
) -> Union[CloudwatchConnection]:

    return _cloudwatch_connection

# 의존성 주입을 위한 컨테이너 생성
application = Container()

# 컨테이너의 구성 요소들을 와이어링합니다.
application.wire(modules=[__name__])

# main 함수 호출하여 Manager 객체 획득
cloudwatch = main()

# 외부로 노출할 변수들을 지정합니다.
__all__ = ['cloudwatch']
