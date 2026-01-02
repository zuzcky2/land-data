from abc import abstractmethod

class AbstractManager:
    """
    드라이버 관리의 추상 클래스입니다. 드라이버가 존재하지 않거나 호출 불가능할 때의 예외 처리를 제공합니다.
    """

    def _raise_driver_not_found(self, driver_name: str):
        """
        드라이버를 찾을 수 없을 때 예외를 발생시킵니다.

        Args:
            driver_name (str): 찾을 수 없는 드라이버의 이름

        Raises:
            ValueError: 드라이버를 찾을 수 없는 경우 예외를 발생시킵니다.
        """
        # 드라이버가 존재하지 않는 경우 ValueError를 발생시킵니다.
        raise ValueError(f"{driver_name} 드라이버가 존재하지 않습니다.")

    def _raise_is_not_callable_class(self, class_name: str):
        """
        클래스가 호출 가능한지 확인할 때 호출 불가능한 경우 예외를 발생시킵니다.

        Args:
            class_name (str): 호출 불가능한 클래스의 이름

        Raises:
            TypeError: 클래스가 호출 불가능한 경우 예외를 발생시킵니다.
        """
        # 클래스가 호출 가능한 클래스가 아닌 경우 TypeError를 발생시킵니다.
        raise TypeError(f"{class_name}는 호출 가능한 클래스가 아닙니다.")

    def _raise_does_not_exist(self, class_name: str):
        """
        클래스가 존재하지 않을 때 예외를 발생시킵니다.

        Args:
            class_name (str): 존재하지 않는 클래스의 이름

        Raises:
            NameError: 클래스가 존재하지 않는 경우 예외를 발생시킵니다.
        """
        # 클래스가 존재하지 않는 경우 NameError를 발생시킵니다.
        raise NameError(f"{class_name}는 현재 모듈에 존재하지 않습니다.")

    @abstractmethod
    def get_connection_instance(self, class_name: str, dictionary: dict, current_module: dict):
        """
        주어진 클래스 이름과 설정으로 데이터베이스 연결 인스턴스를 생성하여 반환합니다.

        Args:
            class_name (str): 연결 클래스 이름
            dictionary (dict): 연결 설정
            current_module (dict): 클래스 목록

        Returns:
            Any: 연결 인스턴스

        Raises:
            TypeError: 클래스가 호출 불가능한 경우 예외를 발생시킵니다.
            NameError: 클래스가 존재하지 않는 경우 예외를 발생시킵니다.
        """

        # 클래스가 현재 모듈에 존재하는지 확인합니다.
        if class_name in current_module:
            connection_class = current_module[class_name]

            # 클래스가 호출 가능한지 확인합니다.
            if callable(connection_class):
                connection_instance = connection_class()
                connection_instance.set_connection(dictionary)
                return connection_instance
            else:
                self._raise_is_not_callable_class(class_name)
        else:
            self._raise_does_not_exist(class_name)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['AbstractManager']
