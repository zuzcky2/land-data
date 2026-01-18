import os
from typing import List
from app.services.location.raw.drivers.abstract_text_driver import AbstractTextDriver


class BlockAddressTextDriver(AbstractTextDriver):

    @property
    def file_prefix(self) -> str:
        return '지번_'

    def _fetch_raw(self, single: bool = False) -> List[dict]:
        """인자에 따라 파일 목록 조회 또는 파일 내용 파싱을 수행합니다."""
        file_path = self.arguments('file_path')
        directory_path = self.arguments('directory_path')

        # 1. 디렉토리 경로가 들어온 경우: 파일 목록 반환 (서비스의 get_import_target_files 대응)
        if directory_path:
            # 부모 클래스(AbstractTextDriver)에 정의한 get_file_list 활용
            files = self.get_file_list(directory_path, prefix=self.file_prefix)
            # 서비스에서 [item['file_path'] for item in pagination.items] 로 쓰므로 형식을 맞춤
            return [{'file_path': f} for f in files]

        # 2. 파일 경로가 들어온 경우: 파일 내용 파싱 (서비스의 import_single_file 대응)
        if file_path and os.path.exists(file_path):
            results = []
            lines = self.read_file_lines(file_path)

            for line in lines:
                if not line: continue

                parts = line.split('|')
                if len(parts) < 11:
                    continue

                bd_mgt_sn = parts[0]
                serial_no = parts[1]

                results.append({
                    'block_address_id': f"{bd_mgt_sn}_{serial_no}",
                    'road_address_id': bd_mgt_sn,
                    'serial_no': serial_no,
                    'bjd_code': parts[2],
                    'si_nm': parts[3],
                    'sgg_nm': parts[4],
                    'emd_nm': parts[5],
                    'li_nm': parts[6],
                    'mountain_yn': parts[7],
                    'lnbr_mnnm': parts[8],
                    'lnbr_slno': parts[9],
                    'representative_yn': parts[10]
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
            with open(file_path, 'rb') as f:
                return sum(line.count(b'\n') for line in f)

        return 0