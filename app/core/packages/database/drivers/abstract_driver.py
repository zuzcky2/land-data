from abc import ABC, abstractmethod


class AbstractDriver(ABC):
    """
    데이터베이스 연결을 관리하기 위한 추상 클래스입니다.
    """
    @abstractmethod
    def set_connection(self, conn: dict):
        """
        데이터베이스에 연결을 설정하는 추상 메서드입니다.
        """
        pass

    @abstractmethod
    def get_connection(self):
        """
        데이터베이스 연결 객체를 반환하는 추상 메서드입니다.
        """
        pass

    def _raise_not_prepare_connection(self):
        """
        연결이 준비되지 않았을 때 ValueError를 발생시킵니다.

        Raises:
            ValueError: 연결이 준비되지 않은 경우 예외를 발생시킵니다.
        """
        raise ValueError('데이터베이스 연결이 준비되지 않았습니다.')


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['AbstractDriver']
