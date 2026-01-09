import ast
import os
import re
import click
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.facade import command
from app.services.location.raw import facade as address_facade
from app.services.location.raw.services.address_service import AddressService
from app.services.building.raw import facade as building_facade
from app.features.contracts.command import AbstractCommand
from app.core.helpers.log import Log

class LocationAddressCommand(AbstractCommand):

    def _get_last_sync_point(self, service: AddressService, source_type: str, renew_days: int = 30) -> Optional[dict]:
        """로그 파일 분석을 통해 소스 타입별 마지막 처리 지점을 반환합니다."""
        try:
            from app.core.helpers.config import Config
            from app.core.helpers.env import Env

            full_logger_name = f"{service.logger_name}_{source_type}"
            logger_config = Config.get(f'logging.{full_logger_name}')

            if not logger_config:
                logger_config = Config.get(f'logging.{service.logger_name}')

            log_path = Env.get('LOG_PATH', '/var/volumes/log')
            log_filename = os.path.join(log_path, logger_config['filename'])

            if not os.path.exists(log_filename):
                return None

            with open(log_filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-100:]
                for line in reversed(lines):
                    if "Sync Start: " in line:
                        date_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                        if date_match:
                            log_time = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S")
                            if datetime.now() - log_time > timedelta(days=renew_days):
                                command.message(f"⚠️ {source_type} 로그 기록이 {renew_days}일을 초과하여 처음부터 시작합니다.", fg='yellow')
                                return None

                        param_match = re.search(r"Sync Start: (\{.*\})", line)
                        if param_match:
                            return ast.literal_eval(param_match.group(1))
        except Exception as e:
            command.message(f"⚠️ {source_type} 로그 분석 오류: {e}", fg='yellow')
        return None

    def sync_address_by_building_info(self, source_type: str, is_continue: bool = False, is_renew: bool = False):
        """건축물대장 기반 주소 마스터 동기화 로직"""
        service = address_facade.address_service

        if source_type == 'group':
            building_service = building_facade.group_info_service
            msg_prefix = "🏢 [총괄표제부]"
        else:
            building_service = building_facade.title_info_service
            msg_prefix = "🏠 [표제부]"

        per_page = 1000
        total_count = 0
        last_id = None

        if is_continue:
            renew_threshold = 7 if is_renew else 9999
            last_point = self._get_last_sync_point(service, source_type, renew_threshold)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try:
                    last_id = ObjectId(last_point['_id'])
                except:
                    last_id = last_point['_id']
                command.message(f"🔄 {msg_prefix} 이어하기: {last_id} 이후부터 시작합니다.", fg='magenta')

        command.message(f"🚀 {msg_prefix} 기반 주소 마스터 수집을 시작합니다.", fg='green')

        while True:
            query_params = {
                'page': 1,
                'per_page': per_page,
                'sort': [('_id', 1)]
            }

            if last_id:
                query_params['_id'] = {'$gt': last_id}

            if source_type == 'title':
                query_params['bun'] = {'$ne': '0000'}
                query_params['regstrKindCd'] = '2'

            pagination = building_service.get_list(query_params, driver_name='mongodb')
            items = pagination.items or []

            if not items:
                command.message(f"✅ {msg_prefix} 모든 데이터를 처리했습니다.", fg='blue')
                break

            for item in items:
                try:
                    keyword = item.get('newPlatPlc', '').strip() or item.get('platPlc', '').strip()
                    if not keyword:
                        last_id = item['_id']
                        continue

                    sync_params = {
                        '_id': str(item['_id']),
                        'block_address': item.get('platPlc'),
                        'road_address': item.get('newPlatPlc'),
                        'mgmBldrgstPk': item.get('mgmBldrgstPk'),
                        'bldNm': item.get('bldNm')
                    }

                    result = service.sync_from_jgk(sync_params, source=source_type)

                    update_data = {}
                    if result.get('status') == 'success' and result.get('bdMgtSn'):
                        update_data['bdMgtSn'] = result['bdMgtSn']
                    elif result.get('status') == 'fail' and result.get('dead'):
                        update_data['dead'] = True

                    if update_data:
                        building_service.manager.driver('mongodb').collection.update_one(
                            {'_id': item['_id']},
                            {'$set': update_data}
                        )

                    last_id = item['_id']
                    total_count += 1

                    if total_count % 50 == 0:
                        command.message(f"  -> {msg_prefix} {total_count}건 처리 완료 (ID: {last_id})", fg='white')

                except Exception as e:
                    command.message(f"❌ PK {item.get('mgmBldrgstPk')} 에러: {e}", fg='red')
                    last_id = item['_id']
                    continue

            if len(items) < per_page:
                break

            time.sleep(0.05)

    def handle_sync_all(self, is_continue: bool = False, is_renew: bool = False):
        """총괄 및 표제부 순차 동기화"""
        command.message("📅 스케줄러: 주소 동기화 작업을 시작합니다.", fg='cyan')
        start_time = time.time()

        self.sync_address_by_building_info('group', is_continue, is_renew)
        self.sync_address_by_building_info('title', is_continue, is_renew)

        total_time = int(time.time() - start_time)
        command.message(f"✨ 전체 동기화 완료 (총 소요시간: {total_time}초)", fg='white', bg='blue')

    def register_commands(self, cli_group):
        """Sync 관련 CLI 명령어 등록"""
        @cli_group.command('location_raw:sync_address_by_group')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_group(is_continue, is_renew):
            self.sync_address_by_building_info('group', is_continue, is_renew)

        @cli_group.command('location_raw:sync_address_by_title')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_title(is_continue, is_renew):
            self.sync_address_by_building_info('title', is_continue, is_renew)

        @cli_group.command('location_raw:sync_address_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_all_cmd(is_continue, is_renew):
            self.handle_sync_all(is_continue, is_renew)

__all__ = ['LocationAddressCommand']