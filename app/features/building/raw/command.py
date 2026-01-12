import ast
import os
import re
import click
import time
from multiprocessing import Process
from datetime import datetime, timedelta
from typing import Optional, List, Any, Dict

from app.services.building.raw import facade as raw_facade
from app.services.building.raw.services.abstract_service import AbstractService
from app.services.location.boundary import facade as boundary_facade
from app.features.contracts.command import AbstractCommand


class BuildingRawCommand(AbstractCommand):

    def _get_last_sync_point(self, service: AbstractService, renew_days: int = 7) -> Optional[dict]:
        """
        로그 파일을 분석하여 마지막 성공 지점을 반환합니다.
        --renew 옵션이 활성화된 경우, 마지막 로그 시간이 renew_days보다 오래되면 처음부터 시작합니다.
        """
        try:
            from app.core.helpers.config import Config
            from app.core.helpers.env import Env

            logger_name = service.logger_name
            logger_config = Config.get(f'logging.{logger_name}')
            log_path = Env.get('LOG_PATH', '/var/volumes/log')
            log_filename = os.path.join(log_path, logger_config['filename'])

            if not os.path.exists(log_filename):
                return None

            with open(log_filename, 'r', encoding='utf-8') as f:
                # 파일의 마지막 100줄을 읽어 역순으로 탐색
                lines = f.readlines()[-100:]
                for line in reversed(lines):
                    if "Sync Start: " in line:
                        # 1. 타임스탬프 파싱 (형식: 2026-01-04 20:20:16)
                        date_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                        if date_match:
                            log_time = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S")

                            # 일주일 경과 확인
                            if datetime.now() - log_time > timedelta(days=renew_days):
                                self.message(f"⚠️ 마지막 로그 기록({log_time})이 {renew_days}일을 초과하여 처음부터 다시 시작합니다.",
                                                fg='yellow')
                                return None

                        # 2. 파라미터 추출
                        param_match = re.search(r"Sync Start: (\{.*\})", line)
                        if param_match:
                            return ast.literal_eval(param_match.group(1))

        except Exception as e:
            self.message(f"⚠️ 로그 분석 중 오류 발생: {e}", fg='yellow')

        return None

    def sync_building_registers_by_township(self, service: AbstractService, is_continue: bool = False,
                                            is_renew: bool = False):
        """
        DB에 저장된 모든 법정동(Township) 목록을 순회하며 갱신합니다.
        """
        self._send_slack(f"🚀 [{service.logger_name}] 수집 프로세스 구동")

        try:
            current_township_page = 1
            per_page = 100
            total_synced_townships = 0

            # 이어하기 지점 파악
            start_item_code = None
            if is_continue:
                # renew 옵션이 있으면 7일 기준 적용, 없으면 무조건 이어하기
                renew_threshold = 7 if is_renew else 9999
                last_point = self._get_last_sync_point(service, renew_threshold)

                if last_point:
                    # sigunguCd(5) + bjdongCd(앞3) 조합으로 8자리 item_code 생성
                    start_item_code = f"{last_point['sigunguCd']}{last_point['bjdongCd'][:3]}"
                    self.message(f"🔄 이어하기 모드: {start_item_code} 지점부터 시작합니다.", fg='magenta')

            self.message('🚀 전국의 모든 법정동 순회 및 건축물대장 수집을 시작합니다.', fg='green')

            while True:
                # 1. 법정동 목록 조회 쿼리
                query_params = {
                    'location_type': 'township',
                    'page': current_township_page,
                    'per_page': per_page
                }

                # 이어하기 조건 적용 ($gte: Greater than or Equal)
                if start_item_code:
                    query_params['item_code'] = {'$gte': start_item_code}

                township_pagination = boundary_facade.service.get_boundaries(
                    params=query_params,
                    driver_name='mongodb'
                )

                items = getattr(township_pagination, 'items', [])

                if not items:
                    self.message(f"--- 더 이상 가져올 법정동 데이터가 없습니다. (Page: {current_township_page}) ---", fg='yellow')
                    break

                for township in items:
                    full_code = township.item_code
                    sigungu_cd = full_code[:5]
                    bjdong_cd = f"{full_code[5:8]}00"

                    self.message(f"📦 [{township.item_full_name}] 수집 시작...", fg='cyan')
                    self._sync_all_pages_for_township(service, sigungu_cd, bjdong_cd)
                    total_synced_townships += 1

                items_count = len(items)
                self.message(f"--- 법정동 목록 {current_township_page} 페이지 완료 ({items_count}개 처리) ---", fg='yellow')

                if items_count < per_page:
                    break

                current_township_page += 1

            self.message(f'✅ 전체 {total_synced_townships}개 법정동 수집 완료!', fg='blue')
            self._send_slack(f"✅ [{service.logger_name}] 완료 (총 {total_synced_townships}개 법정동)")

        except Exception as e:
            self._handle_error(e, f"일괄 수집 프로세스 중단 @see {__file__}")

    def _sync_all_pages_for_township(self, service: AbstractService, sigungu_cd: str, bjdong_cd: str):
        """특정 법정동의 데이터를 마지막 페이지까지 강제로 순회하며 가져옵니다."""
        current_page = 1
        per_page = 100

        while True:
            sync_result = service.sync_from_dgk({
                'sigunguCd': sigungu_cd,
                'bjdongCd': bjdong_cd,
                'page': current_page,
                'per_page': per_page
            })

            # 에러 발생 시 중단 (AbstractService에서 status='error' 반환 가정)
            if sync_result.get('status') == 'error':
                break

            items_count = sync_result.get('count', 0)

            if items_count > 0:
                self.message(f"  -> {current_page}p: {items_count}건 완료", fg='white')

            # 탈출 조건
            if items_count == 0 or items_count < per_page or current_page >= 100:
                break

            current_page += 1

    def handle_sync_all(self, is_continue: bool, is_renew: bool):
        """
        스케줄러와 CLI 양쪽에서 호출할 수 있는 공통 실행 메서드
        """
        services = [
            (raw_facade.group_info_service, "총괄표제부"),
            (raw_facade.title_info_service, "표제부"),
            (raw_facade.basic_info_service, "기본정보"),
            (raw_facade.floor_info_service, "층정보"),
            (raw_facade.area_info_service, "면적정보"),
            (raw_facade.price_info_service, "가격정보"),
            (raw_facade.address_info_service, "주소정보"),
            (raw_facade.relation_info_service, "지번관계"),
            (raw_facade.zone_info_service, "지역지구"),
        ]

        self.message(f'🔥 전체 데이터 병렬 수집 시작 (Continue={is_continue}, Renew={is_renew})', fg='green')
        self._send_slack(f"🔥 전체 수집 대장정 시작 (Continue={is_continue})")

        chunk_size = 3
        for i in range(0, len(services), chunk_size):
            current_chunk = services[i:i + chunk_size]
            processes = []

            for service_obj, service_name in current_chunk:
                self.message(f"🚀 [병렬 시작] {service_name} 프로세스 구동", fg='cyan')
                p = Process(
                    target=self.sync_building_registers_by_township,
                    args=(service_obj, is_continue, is_renew)
                )
                p.start()
                processes.append(p)

            for p in processes:
                p.join()

            self.message(f"✅ 그룹 수집 완료. 다음으로 이동합니다.", fg='yellow')

        self.message('🏁 모든 데이터 수집 대장정 완료!', fg='blue')
        self._send_slack("🏁 건축물대장 모든 데이터 수집 대장정 완료")

    def register_commands(self, cli_group):
        """CLI 그룹에 명령어 등록"""

        def create_sync_command(name, service_obj, help_text):
            @cli_group.command(name, help=help_text)
            @click.option('--continue', 'is_continue', is_flag=True, help='마지막 로그 지점부터 이어서 수집합니다.')
            @click.option('--renew', 'is_renew', is_flag=True, help='일주일 이상된 로그면 처음부터 수집합니다.')
            def _command(is_continue, is_renew):
                self.sync_building_registers_by_township(service_obj, is_continue, is_renew)

        # 9개 개별 커맨드 등록
        create_sync_command('building_raw:group_info', raw_facade.group_info_service, '총괄표제부 수집')
        create_sync_command('building_raw:title_info', raw_facade.title_info_service, '표제부 수집')
        create_sync_command('building_raw:basic_info', raw_facade.basic_info_service, '기본정보 수집')
        create_sync_command('building_raw:floor_info', raw_facade.floor_info_service, '층정보 수집')
        create_sync_command('building_raw:area_info', raw_facade.area_info_service, '면적정보 수집')
        create_sync_command('building_raw:price_info', raw_facade.price_info_service, '가격정보 수집')
        create_sync_command('building_raw:address_info', raw_facade.address_info_service, '주소정보 수집')
        create_sync_command('building_raw:relation_info', raw_facade.relation_info_service, '지번관계 수집')
        create_sync_command('building_raw:zone_info', raw_facade.zone_info_service, '지역지구 수집')

        @cli_group.command('building_raw:all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_all_cli(is_continue, is_renew):
            # 추출한 공통 메서드 호출
            self.handle_sync_all(is_continue, is_renew)


__all__ = ['BuildingRawCommand']