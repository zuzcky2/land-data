from abc import abstractmethod

class AbstractProvider:
    """
    ProviderAbstract 클래스는 구현체에서 구현해야 하는 추상 메서드를 정의합니다.
    """

    @abstractmethod
    def boot(self):
        """
        Provider 를 부팅하는 추상 메서드입니다.
        구현체에서 이 메서드를 구현해야 합니다.
        """
        pass

# 외부로 노출할 변수들을 지정합니다.
__all__ = ['AbstractProvider']