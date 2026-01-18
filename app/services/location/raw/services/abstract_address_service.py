import os
import logging
import glob
from abc import abstractmethod
from typing import List, Union

from app.services.location.raw.managers.abstract_manager import AbstractManager
from app.services.location.raw.managers.block_address_manager import BlockAddressManager
from app.services.location.raw.managers.building_group_manager import BuildingGroupManager
from app.services.location.raw.managers.road_address_manager import RoadAddressManager
from app.services.location.raw.services.abstract_service import AbstractService

class AbstractAddressService(AbstractService):

    @property
    @abstractmethod
    def logger_name(self) -> str:
        """자식 클래스에서 정의할 로거 이름"""
        pass

    @property
    @abstractmethod
    def manager(self) -> Union[AbstractManager, BlockAddressManager, RoadAddressManager, BuildingGroupManager]:
        pass

    def should_process_file(self, file_path: str) -> bool:
        """
        FINISH 또는 SKIP 로그를 확인하여 파일 처리 여부를 결정합니다.
        logrotate된 파일까지 모두 검사합니다.
        """
        current_mtime = int(os.path.getmtime(file_path))
        file_name = os.path.basename(file_path)

        patterns = [
            f"✅ FINISH: {file_name} (mtime: {current_mtime})",
            f"⏭️  SKIP: {file_name} (mtime: {current_mtime})"
        ]

        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                base_log_path = handler.baseFilename
                log_files = [base_log_path] + glob.glob(f"{base_log_path}.*")

                for log_file in log_files:
                    if not os.path.exists(log_file):
                        continue
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if any(pattern in content for pattern in patterns):
                                return False
                    except Exception:
                        continue
        return True

    def get_import_target_files(self, directory_path: str) -> List[str]:
        """디렉토리 내 파일 목록을 추출합니다."""
        pagination = self.manager.text_driver.clear().set_arguments({
            'directory_path': directory_path
        }).read()

        items = pagination.items
        return [item['file_path'] for item in items if os.path.basename(item['file_path'])]

    def import_single_file(self, file_path: str) -> int:
        """공통 임포트 프로세스 (체크 -> 읽기 -> 저장 -> 로그)"""
        file_name = os.path.basename(file_path)
        current_mtime = int(os.path.getmtime(file_path))

        if not self.should_process_file(file_path):
            self.logger.info(f"⏭️  SKIP: {file_name} (mtime: {current_mtime}) (이미 처리됨)")
            return 0

        self.logger.info(f"🚀 START: {file_name} 임포트 시작 (mtime: {current_mtime})")

        try:
            pagination = self.manager.text_driver.clear().set_arguments({
                'file_path': file_path
            }).read()

            all_items = pagination.items

            if not all_items:
                self.logger.info(f"✅ FINISH: {file_name} (mtime: {current_mtime}) (0건)")
                return 0

            self.manager.mongodb_driver.store(all_items)
            total_saved = len(all_items)

            self.logger.info(f"✅ FINISH: {file_name} (mtime: {current_mtime}) (총 {total_saved}건)")
            return total_saved

        except Exception as e:
            self.logger.error(f"❌ ERROR: {file_name} - {str(e)}")
            raise e