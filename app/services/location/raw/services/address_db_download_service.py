import os
import requests
import zipfile
import shutil
import glob
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from app.core.helpers.config import Config
from app.core.helpers.log import Log


class AddressDBDownloadService:
    def __init__(self):
        self.logger = Log.get_logger('location_raw_address_db')
        self.base_dir = f"{Config.get('app.project_root')}/resources/juso_go_kr/address_db"
        self.current_dir = os.path.join(self.base_dir, "current")
        self.base_url = "https://business.juso.go.kr/api/jst/download"

    def run(self):
        """서비스 메인 실행 로직"""
        target_info = self._find_available_data()
        if not target_info:
            self.logger.error("다운로드 가능한 데이터를 찾을 수 없습니다.")
            return

        url, file_name = target_info
        dest_path = os.path.join(self.base_dir, file_name)

        # 1. 파일 다운로드 단계
        downloaded = False
        if os.path.exists(dest_path):
            self.logger.info(f"⏭️  SKIP: 이미 파일이 존재합니다. ({file_name})")
            downloaded = True  # 이미 있으므로 성공으로 간주
        else:
            if self._download_file(url, dest_path):
                downloaded = True

        # 2. 압축 해제 판단 (다운로드 성공했거나, 파일은 있는데 current가 없는 경우)
        if downloaded:
            should_extract = False

            if not os.path.exists(self.current_dir):
                self.logger.info("📂 current 디렉토리가 없어 압축 해제를 진행합니다.")
                should_extract = True
            elif not os.listdir(self.current_dir):
                self.logger.info("📂 current 디렉토리가 비어 있어 압축 해제를 진행합니다.")
                should_extract = True

            # 파일이 방금 다운로드되었거나, 위 조건에 의해 해제가 필요한 경우
            # (방금 다운로드된 경우는 항상 current를 최신화하기 위해 실행)
            if should_extract or not os.path.exists(os.path.join(self.base_dir, ".last_extracted_" + file_name)):
                self._extract_to_current(dest_path)
                # 동일 파일 중복 해제 방지를 위한 마킹 (선택 사항)
                self._mark_as_extracted(file_name)

            # 3. 오래된 파일 정리
            self._cleanup_old_files()

    def _find_available_data(self) -> Optional[Tuple[str, str]]:
        now = datetime.now()
        for i in range(12):
            target_date = now - timedelta(days=30 * i)
            year = target_date.strftime('%Y')
            year_month = target_date.strftime('%Y%m')

            file_name = f"{year_month}_주소DB_전체분.zip"
            real_file_name = f"{year_month}ALLMTCHG00.zip"

            params = {
                'regYmd': year, 'reqType': 'ALLMTCHG', 'ctprvnCd': '00',
                'stdde': year_month, 'fileName': file_name, 'realFileName': real_file_name,
                'intFileNo': '0', 'intNum': '0'
            }
            query_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{self.base_url}?{query_string}"

            try:
                # 데이터 존재 확인
                response = requests.head(full_url, timeout=10)
                if response.status_code == 200:
                    return full_url, file_name
            except Exception:
                continue
        return None

    def _download_file(self, url: str, dest_path: str) -> bool:
        try:
            self.logger.info(f"📥 다운로드 시작: {url}")
            os.makedirs(self.base_dir, exist_ok=True)
            with requests.get(url, stream=True, timeout=120) as r:
                r.raise_for_status()
                with open(dest_path, 'wb') as f:
                    shutil.copyfileobj(r.raw, f)
            self.logger.info(f"✅ 다운로드 완료: {dest_path}")
            return True
        except Exception as e:
            self.logger.error(f"❌ 다운로드 실패: {str(e)}")
            return False

    def _extract_to_current(self, zip_path: str):
        """한글 파일명 깨짐 및 charmap 에러 방지 로직을 포함한 압축 해제"""
        try:
            self.logger.info(f"📦 압축 해제 시작: {os.path.basename(zip_path)}")

            if os.path.exists(self.current_dir):
                shutil.rmtree(self.current_dir)
            os.makedirs(self.current_dir, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                for file_info in zip_ref.infolist():
                    # 💡 CP437 바이트를 CP949로 재해석하여 한글 깨짐 방지
                    try:
                        decoded_name = file_info.filename.encode('cp437').decode('cp949')
                    except:
                        decoded_name = file_info.filename

                    target_path = os.path.join(self.current_dir, decoded_name)

                    if file_info.is_dir():
                        os.makedirs(target_path, exist_ok=True)
                        continue

                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_ref.open(file_info) as source, open(target_path, 'wb') as target:
                        shutil.copyfileobj(source, target)

            self.logger.info("✨ current 디렉토리 압축 해제 완료")
        except Exception as e:
            self.logger.error(f"❌ 압축 해제 오류: {str(e)}")

    def _mark_as_extracted(self, file_name: str):
        """해제 완료 마킹 (동일 파일 중복 해제 방지용)"""
        marker = os.path.join(self.base_dir, f".last_extracted_{file_name}")
        # 기존 마커들 삭제
        for f in glob.glob(os.path.join(self.base_dir, ".last_extracted_*")):
            os.remove(f)
        with open(marker, 'w') as f:
            f.write(datetime.now().isoformat())

    def _cleanup_old_files(self):
        """최근 3개 ZIP 파일 유지"""
        zip_files = sorted(glob.glob(os.path.join(self.base_dir, "*.zip")), reverse=True)
        if len(zip_files) > 3:
            for old_file in zip_files[3:]:
                os.remove(old_file)
                self.logger.info(f"🗑️ 오래된 파일 삭제: {os.path.basename(old_file)}")