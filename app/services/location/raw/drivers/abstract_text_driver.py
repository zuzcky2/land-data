import os
from abc import ABC, abstractmethod
from typing import List, Generator
import unicodedata
from app.services.location.raw.drivers.driver_interface import DriverInterface


class AbstractTextDriver(DriverInterface, ABC):

    @property
    @abstractmethod
    def file_prefix(self) -> str:
        pass


    def read_file_lines(self, file_path: str) -> Generator[str, None, None]:
        """인코딩을 명시적으로 cp949로 고정하되, 깨지는 문자는 무시하고 루프를 유지합니다."""
        if not os.path.exists(file_path):
            return

        # 💡 'replace' 옵션은 깨진 바이트를 '?'로 치환하여 루프가 중단되지 않게 합니다.
        # 한국 공공데이터 텍스트 파일은 cp949가 표준입니다.
        with open(file_path, 'r', encoding='cp949', errors='replace') as f:
            for line in f:
                yield line.strip()

    def get_file_list(self, directory: str, prefix: str = "") -> List[str]:
        """
        NFC(완성형)와 NFD(조합형) 프리픽스를 모두 허용하여 파일 목록을 추출합니다.
        """
        if not os.path.isdir(directory):
            return []

        # 1. 입력받은 프리픽스를 완성형(NFC)과 조합형(NFD) 두 버전으로 준비
        nfc_prefix = unicodedata.normalize('NFC', prefix)
        nfd_prefix = unicodedata.normalize('NFD', prefix)

        file_list = []
        for f in os.listdir(directory):
            # 확장자 체크
            if not f.endswith('.txt'):
                continue

            # 2. 파일명 f가 완성형 프리픽스나 조합형 프리픽스 중 하나로 시작하는지 확인
            # (또는 f를 정규화해서 비교해도 되지만, 두 패턴을 모두 체크하는 것이 더 직관적입니다)
            if f.startswith(nfc_prefix) or f.startswith(nfd_prefix):
                file_list.append(os.path.join(directory, f))

        return sorted(file_list)

    def store(self, items: List[dict]):
        raise NotImplementedError("Text 드라이버는 저장 기능을 지원하지 않습니다.")