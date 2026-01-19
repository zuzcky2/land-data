import os
from typing import List
from app.services.location.raw.drivers.abstract_text_driver import AbstractTextDriver


class RoadCodeTextDriver(AbstractTextDriver):

    @property
    def file_prefix(self) -> str:
        return '개선_도로명코드_'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        """도로명코드 파일 파싱 (변경사유 및 이력정보 포함)"""
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        # 1. 디렉토리 경로가 들어온 경우: 파일 목록 반환
        if directory_path:
            files = self.get_file_list(directory_path, prefix=self.file_prefix)
            return [{'file_path': f} for f in files]

        # 2. 파일 경로가 들어온 경우: 데이터 파싱
        if file_path and os.path.exists(file_path):
            results = []
            lines = self.read_file_lines(file_path)

            for line in lines:
                if not line: continue

                parts = line.split('|')
                # 17번 컬럼(말소일자)까지 있으므로 최소 17개 이상의 컬럼 확인
                if len(parts) < 17:
                    continue

                # 데이터 매핑 (인덱스는 0부터 시작)
                road_code      = parts[0]   # 0: 도로명코드 (12자리)
                road_nm        = parts[1]   # 1: 도로명
                road_nm_eng    = parts[2]   # 2: 도로명 로마자
                emd_sn         = parts[3]   # 3: 읍면동일련번호 (2자리)
                sido_nm        = parts[4]   # 4: 시도명
                sido_nm_eng    = parts[5]   # 5: 시도명 로마자
                sgg_nm         = parts[6]   # 6: 시군구명
                sgg_nm_eng     = parts[7]   # 7: 시군구명 로마자
                emd_nm         = parts[8]   # 8: 읍면동명
                emd_nm_eng     = parts[9]   # 9: 읍면동명 로마자
                emd_se         = parts[10]  # 10: 읍면동구분
                emd_code       = parts[11]  # 11: 읍면동코드
                use_yn         = parts[12]  # 12: 사용여부
                change_reason  = parts[13]  # 13: 변경사유 (0~4, 9)
                change_history = parts[14]  # 14: 변경이력정보
                notice_date    = parts[15]  # 15: 고시일자 (YYYYMMDD)
                expire_date    = parts[16]  # 16: 말소일자 (YYYYMMDD)

                # PK 결론: 데이터 유실 방지를 위한 조합형 ID
                road_code_id = f"{road_code}_{emd_sn}"

                results.append({
                    'road_code_id': road_code_id,
                    'road_code': road_code,
                    'road_nm': road_nm,
                    'road_nm_eng': road_nm_eng,
                    'emd_sn': emd_sn,
                    'sido_nm': sido_nm,
                    'sido_nm_eng': sido_nm_eng,
                    'sgg_nm': sgg_nm,
                    'sgg_nm_eng': sgg_nm_eng,
                    'emd_nm': emd_nm,
                    'emd_nm_eng': emd_nm_eng,
                    'emd_se': emd_se,
                    'emd_code': emd_code,
                    'use_yn': use_yn,
                    'change_reason': change_reason,
                    'change_history': change_history,
                    'notice_date': notice_date,
                    'expire_date': expire_date
                })

                if single:
                    break

            return results

        return []

    def _get_total_count(self) -> int:
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        if directory_path:
            return len(self.get_file_list(directory_path, prefix=self.file_prefix))

        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return sum(line.count(b'\n') for line in f)

        return 0