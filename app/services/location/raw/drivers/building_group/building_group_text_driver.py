import os
from typing import List
from app.services.location.raw.drivers.abstract_text_driver import AbstractTextDriver


class BuildingGroupTextDriver(AbstractTextDriver):

    @property
    def file_prefix(self) -> str:
        return '부가정보_'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        """인자에 따라 파일 목록 조회 또는 부가정보(building_group) 내용 파싱을 수행합니다."""
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        # 1. 디렉토리 경로가 들어온 경우: 파일 목록 반환
        if directory_path:
            files = self.get_file_list(directory_path, prefix=self.file_prefix)
            return [{'file_path': f} for f in files]

        # 2. 파일 경로가 들어온 경우: 부가정보 내용 파싱
        if file_path and os.path.exists(file_path):
            results = []
            # AbstractTextDriver의 인코딩 방어 로직 사용 (cp949 대응)
            lines = self.read_file_lines(file_path)

            for line in lines:
                if not line: continue

                parts = line.split('|')
                # 부가정보 레이아웃 기준 컬럼 수 체크 (9개)
                if len(parts) < 9:
                    continue

                # 이미지(부가정보) 정의서 기반 매핑
                manage_no      = parts[0]  # 관리번호 (PK)
                h_dong_code    = parts[1]  # 행정동코드
                h_dong_nm      = parts[2]  # 행정동명
                zip_code       = parts[3]  # 우편번호
                zip_serial_no  = parts[4]  # 우편번호 일련번호
                mass_dlv_nm    = parts[5]  # 다량배달처명
                build_nm       = parts[6]  # 건축물대장 건물명
                sgg_build_nm   = parts[7]  # 시군구 건물명
                is_apartment   = parts[8]  # 공동주택여부 (0:비공동, 1:공동)

                results.append({
                    'road_address_id': manage_no,
                    'h_dong_code': h_dong_code,
                    'h_dong_nm': h_dong_nm,
                    'zip_code': zip_code,
                    'zip_serial_no': zip_serial_no,
                    'mass_dlv_nm': mass_dlv_nm,
                    'build_nm': build_nm,
                    'sgg_build_nm': sgg_build_nm,
                    'is_apartment': is_apartment
                })

                if single:
                    break

            return results

        return []

    def _get_total_count(self) -> int:
        """목록 조회일 때는 파일 개수를, 파싱일 때는 행 수를 반환합니다."""
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        if directory_path:
            return len(self.get_file_list(directory_path, prefix=self.file_prefix))

        if file_path and os.path.exists(file_path):
            # 대용량 파일 대응을 위해 Binary 모드로 행 수 계산
            with open(file_path, 'rb') as f:
                return sum(line.count(b'\n') for line in f)

        return 0