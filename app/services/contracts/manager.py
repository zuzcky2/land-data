from abc import ABC, abstractmethod
from typing import Dict, Generic, TypeVar, Optional

T = TypeVar("T")


class AbstractManager(ABC, Generic[T]):

    @abstractmethod
    def get_default_driver(self) -> str:
        """기본 드라이버 이름을 반환합니다."""
        pass

    @abstractmethod
    def driver(self, name: Optional[str] = None) -> T:
        """드라이버 인스턴스를 반환 (싱글톤)"""
        name = name or self.get_default_driver()

        return self._create_driver(name)

    def _create_driver(self, name: str) -> T:
        """드라이버 생성 로직 분기"""

        # 2. create_{name}_driver 메서드가 정의되어 있는지 확인
        method_name = f"_create_{name}_driver"
        if hasattr(self, method_name):
            # 메서드를 가져와서 실행
            creator = getattr(self, method_name)
            return creator()

        raise ValueError(f"Driver [{name}] not supported. Method [{method_name}] not found.")

__all__ = ['AbstractManager']