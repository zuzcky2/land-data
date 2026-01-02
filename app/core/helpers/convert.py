from typing import Union, Optional
from click.core import Context, Option
import re

class Convert:
    """
    다양한 데이터 형식 변환을 위한 유틸리티 클래스입니다.
    """

    @staticmethod
    def to_bool(
        ctx: Optional[Context] = None,
        param: Optional[Option] = None,
        value: Union[bool, str, int] = None
    ) -> Optional[bool]:
        """
        주어진 값을 불리언으로 변환합니다.

        Args:
            ctx (Optional[Context]): Click 컨텍스트 객체입니다.
            param (Optional[Option]): Click 옵션 객체입니다.
            value (Union[bool, str, int]): 변환할 값입니다.

        Returns:
            Optional[bool]: 변환된 불리언 값. 변환할 수 없는 경우 None을 반환합니다.
        """
        if value is None:
            return None

        # 참/거짓으로 간주되는 값의 목록
        truthy_values = {'1', 'true', 'y', 'yes', True, 1}
        falsy_values = {'0', 'false', 'n', 'no', False, 0}

        # 값을 불리언으로 변환하여 반환
        if value in truthy_values:
            return True
        elif value in falsy_values:
            return False
        return None  # 변환할 수 없는 경우 None 반환

    @staticmethod
    def snake_to_camel(snake_str: str) -> str:
        """
        주어진 snake_case 문자열을 camelCase로 변환합니다.

        Args:
            snake_str (str): 변환할 snake_case 문자열입니다.

        Returns:
            str: 변환된 camelCase 문자열입니다.
        """
        # 첫 단어는 소문자로 유지하고, 이후 밑줄 뒤의 문자는 대문자로 변환하여 결합
        components = snake_str.split('_')
        return components[0] + ''.join(word.title() for word in components[1:])

    @staticmethod
    def camel_to_snake(camel_str: str) -> str:
        """
        주어진 camelCase 문자열을 snake_case로 변환합니다.

        Args:
            camel_str (str): 변환할 camelCase 문자열입니다.

        Returns:
            str: 변환된 snake_case 문자열입니다.
        """
        # 대문자 앞에 밑줄을 추가하고, 모든 문자를 소문자로 변환하여 반환
        return re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()

    @staticmethod
    def capitalize_first_letter(input_str: Optional[str]) -> Optional[str]:
        """
        주어진 문자열의 첫 글자를 대문자로 변환합니다.

        Args:
            input_str (Optional[str]): 첫 글자를 대문자로 변환할 문자열입니다.

        Returns:
            Optional[str]: 첫 글자가 대문자로 변환된 문자열입니다. 입력이 None일 경우 None을 반환합니다.
        """
        # 입력값이 없으면 None 반환
        if not input_str:
            return None

        # 첫 글자를 대문자로 변환하고 나머지 문자를 그대로 유지하여 반환
        return input_str[0].upper() + input_str[1:]

# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['Convert']