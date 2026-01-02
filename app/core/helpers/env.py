import os
from dotenv import dotenv_values
from collections import OrderedDict
from pydantic import Field
from typing import Union, Optional, Any
from str2bool import str2bool
import numpy as np


class Env:
    """
    프로젝트의 환경 변수를 관리하는 클래스입니다.
    .env 파일과 시스템 환경 변수를 결합하여 프로젝트 전반에서 환경 변수를 쉽게 가져올 수 있도록 합니다.

    Attributes:
        __items (OrderedDict): .env 파일과 환경 변수에서 불러온 값들을 포함하는 OrderedDict입니다.
        __cached_values (dict): 접근한 환경 변수 값을 캐싱하여 성능을 최적화하는 딕셔너리입니다.
    """
    __cached_values = {}  # 환경 변수 값을 캐싱하기 위한 딕셔너리입니다.

    __items: OrderedDict = OrderedDict({
        **dict(dotenv_values(f"{os.environ['PROJECT_ROOT']}/.env")),
        **dict(os.environ)
    })

    @staticmethod
    def get(key: Optional[str] = None, default: Any = None) -> Union[str, int, float, None]:
        """
        주어진 키에 해당하는 환경 변수 값을 반환하거나, 키가 없으면 전체 환경 변수 목록을 반환합니다.

        Args:
            key (str, optional): 가져올 환경 변수의 키입니다. 기본값은 None이며, 이 경우 전체 환경 변수 목록을 반환합니다.
            default (Any): 환경 변수가 없을 경우 반환할 기본값입니다.

        Returns:
            Union[str, int, float, None]: 변환된 값, 전체 환경 변수 값 또는 None입니다.
        """
        # 캐시된 값이 있으면 이를 반환
        if key in Env.__cached_values:
            return Env.__cached_values[key]

        # 환경 변수 키가 없을 경우 전체 환경 변수 목록 반환
        if key is None:
            return Env.__items

        # 키가 존재하지 않으면 기본값 반환
        value = Env.__items.get(key, default)
        if value is None:
            return default

        # 값 변환 후 캐시에 저장하여 반환
        converted_value = Env.convert_value(value)
        Env.__cached_values[key] = converted_value
        return converted_value

    @staticmethod
    def convert_value(value: str = Field(title='값', description='.env 특정 키에 정의된 값')) -> Union[
        str, int, float, None]:
        """
        주어진 문자열 값을 적절한 데이터 타입으로 변환합니다.

        Args:
            value (str): 변환할 환경 변수 값입니다.

        Returns:
            Union[str, int, float, None]: 변환된 값 또는 None.

        변환 규칙:
            - 'true' 또는 'false' 문자열은 bool 타입으로 변환합니다.
            - 숫자 문자열은 int 또는 float로 변환합니다.
            - 그 외 값은 그대로 문자열로 반환합니다.
        """
        # true/false 문자열을 bool 타입으로 변환
        if value.lower() in ['true', 'false']:
            return bool(str2bool(value))

        # 숫자인 경우 int 또는 float로 변환
        try:
            num_value = np.float64(value)
            return int(num_value) if num_value.is_integer() else num_value
        except ValueError:
            return value  # 변환할 수 없는 경우 원본 문자열 반환


# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['Env']