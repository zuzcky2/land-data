import os
from typing import List
from app.services.location.raw.drivers.abstract_text_driver import AbstractTextDriver


class RoadAddressTextDriver(AbstractTextDriver):

    @property
    def file_prefix(self) -> str:
        return '주소_'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        """인자에 따라 파일 목록 조회 또는 도로명주소 파일 내용 파싱을 수행합니다."""
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        # 1. 디렉토리 경로가 들어온 경우: 파일 목록 반환
        if directory_path:
            # 부모 클래스에 정의된 로직을 사용하며, 도로명주소 파일은 보통 'build_' 등으로 시작할 수 있습니다.
            # 필요 시 get_file_list의 인자를 조정하세요.
            files = self.get_file_list(directory_path, prefix=self.file_prefix)
            return [{'file_path': f} for f in files]

        # 2. 파일 경로가 들어온 경우: 도로명주소(건물) 데이터 파싱
        if file_path and os.path.exists(file_path):
            results = []
            # 부모 클래스에서 정의한 cp949 기반 Safe Read 사용
            lines = self.read_file_lines(file_path)

            for line in lines:
                if not line: continue

                parts = line.split('|')
                # 이미지 레이아웃 상 11개의 컬럼이 존재함
                if len(parts) < 11:
                    continue

                # 이미지 정의서 기반 매핑
                manage_no = parts[0]      # 관리번호 (PK)
                road_code = parts[1]      # 도로명코드
                emd_serial_no = parts[2]  # 읍면동일련번호
                is_basement = parts[3]    # 지하여부 (0:지상, 1:지하, 2:공중, 3:수상)
                build_mnnm = parts[4]     # 건물본번
                build_slno = parts[5]     # 건물부번
                basic_area_no = parts[6]  # 기초구역번호(우편번호)
                change_reason = parts[7]  # 변경사유코드
                notice_date = parts[8]    # 고시일자
                prev_road_addr = parts[9] # 변경전 도로명주소
                has_detail = parts[10]    # 상세주소 부여여부

                results.append({
                    'road_address_id': manage_no, # 관리번호를 ID로 사용
                    'manage_no': manage_no,
                    'road_code': road_code,
                    'emd_serial_no': emd_serial_no,
                    'is_basement': is_basement,
                    'build_mnnm': int(build_mnnm) if build_mnnm.isdigit() else 0,
                    'build_slno': int(build_slno) if build_slno.isdigit() else 0,
                    'basic_area_no': basic_area_no,
                    'change_reason': change_reason,
                    'notice_date': notice_date,
                    'prev_road_addr': prev_road_addr,
                    'has_detail': has_detail
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
            # 인코딩 이슈를 피하기 위해 Binary 모드로 행 수 계산
            with open(file_path, 'rb') as f:
                return sum(line.count(b'\n') for line in f)

        return 0