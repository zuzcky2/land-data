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

class LocationRawCommand(AbstractCommand):

    def sync_address_by_building_info(self, source_type: str, is_continue: bool = False, is_renew: bool = False):
        """건축물대장 기반 주소 마스터 동기화 로직"""
        service = address_facade.address_service

        if source_type == 'group':
            building_service = building_facade.group_info_service
            msg_prefix = "🏢 [총괄표제부]"
        elif source_type == 'basic':
            building_service = building_facade.basic_info_service
            msg_prefix = "🏢 [기본개요]"
        else:
            building_service = building_facade.title_info_service
            msg_prefix = "🏠 [표제부]"

        self._send_slack(f"🚀 {msg_prefix} 주소 동기화 가동")

        try:
            per_page = 10000
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
                    self.message(f"🔄 {msg_prefix} 이어하기: {last_id} 이후부터 시작합니다.", fg='magenta')

            self.message(f"🚀 {msg_prefix} 기반 주소 마스터 수집을 시작합니다.", fg='green')

            # 수정된지 7일 지난것들만 작업
            now =  datetime.now()
            role_date = now - timedelta(days=7)
            while True:
                query_params = {
                    'page': 1,
                    'per_page': per_page,
                    '$or': [
                        {'updated_at': {'lt': role_date}},
                        {'bdMgtSn': {'$exists': False}},
                        {'bdMgtSn': None},
                    ],
                    'newPlatPlc': {'$nin': ['', None, ' ']},
                    'dead': {'$ne': True},
                    'sort': [('_id', 1)]
                }

                if last_id:
                    query_params['_id'] = {'$gt': last_id}
                elif source_type == 'basic':
                    query_params['mgmUpBldrgstPk'] = '0'
                    query_params['regstrKindCd'] = {'$ne': '4'}

                pagination = building_service.get_list(query_params, driver_name='mongodb')

                items = pagination.items or []

                if not items:
                    self.message(f"✅ {msg_prefix} 모든 데이터를 처리했습니다.", fg='blue')
                    break

                for item in items:
                    try:
                        keyword = item.get('newPlatPlc', '').strip()
                        if not keyword:
                            last_id = item['_id']
                            continue


                        search_queries = [item.get('newPlatPlc')]
                        search_queries = [q for q in search_queries if q]

                        sync_params = {
                            '_id': str(item['_id']),
                            'search_queries': {'$in': search_queries},
                            'updated_at': {'$gt': role_date},
                            'mgmBldrgstPk': item.get('mgmBldrgstPk'),
                            'bldNm': item.get('bldNm')
                        }

                        result = service.sync_from_jgk(sync_params, source=source_type)

                        if result.get('status') == 'success' and result.get('bdMgtSn'):
                            item['bdMgtSn'] = result['bdMgtSn']
                        elif result.get('status') == 'fail' and result.get('dead'):
                            item['dead'] = True

                        building_service.manager.driver('mongodb').store([item])

                        last_id = item['_id']
                        total_count += 1

                        if total_count % 50 == 0:
                            self.message(f"  -> {msg_prefix} {total_count}건 처리 완료 (ID: {last_id})", fg='white')

                    except Exception as e:
                        self.message(f"❌ PK {item.get('mgmBldrgstPk')} 에러: {e}", fg='red')
                        last_id = item['_id']
                        continue

                if len(items) < per_page:
                    break

            self._send_slack(f"✅ {msg_prefix} 완료 (총 {total_count}건)")

        except Exception as e:
            self._handle_error(e, f"{msg_prefix} 주소 동기화 중단")

    def handle_sync_all(self, is_continue: bool = False, is_renew: bool = False):
        """총괄 및 표제부 순차 동기화"""
        self._send_slack("📅 주소 동기화 전체 프로세스 가동")
        self.message("📅 스케줄러: 주소 동기화 작업을 시작합니다.", fg='cyan')
        start_time = time.time()

        self.sync_address_by_building_info('group', is_continue, is_renew)
        self.sync_address_by_building_info('title', is_continue, is_renew)

        total_time = int(time.time() - start_time)
        self.message(f"✨ 전체 동기화 완료 (총 소요시간: {total_time}초)", fg='white', bg='blue')
        self._send_slack(f"✨ 주소 동기화 전체 완료 (소요시간: {total_time}초)")

    def register_commands(self, cli_group):
        """Sync 관련 CLI 명령어 등록"""
        @cli_group.command('location_raw:address_by_group')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_group(is_continue, is_renew):
            self.sync_address_by_building_info('group', is_continue, is_renew)

        @cli_group.command('location_raw:address_by_title')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_title(is_continue, is_renew):
            self.sync_address_by_building_info('title', is_continue, is_renew)

        @cli_group.command('location_raw:address_by_basic')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_title(is_continue, is_renew):
            self.sync_address_by_building_info('basic', is_continue, is_renew)

        @cli_group.command('location_raw:address_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_all_cmd(is_continue, is_renew):
            self.handle_sync_all(is_continue, is_renew)

__all__ = ['LocationRawCommand']