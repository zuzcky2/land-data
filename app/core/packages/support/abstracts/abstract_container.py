from dependency_injector import containers, providers

class AbstractContainer(containers.DeclarativeContainer):
    """
    종속성 주입을 위한 컨테이너 클래스입니다.

    Attributes:
        config (providers.Configuration): 구성 정보를 제공하는 Configuration 객체입니다.
    """
    config: providers.Configuration = providers.Configuration()

# 외부로 노출할 변수들을 지정합니다.
__all__ = ['AbstractContainer', 'providers']