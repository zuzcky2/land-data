import ast
import os
import re
import click
import time
import traceback
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from multiprocessing import Pool

from app.core.helpers.config import Config
from app.services.location.raw import facade as location_raw_facade
from app.services.building.raw import facade as building_facade
from app.features.contracts.command import AbstractCommand


class LocationRawCommand(AbstractCommand):

    @staticmethod
    def _worker_sync_address_task(payload: Dict[str, Any]) -> Dict[str, Any]:
        """각 코어에서 독립적으로 실행될 주소 동기화 태스크"""
        item = payload.get('item')
        source_type = payload.get('source_type')
        role_date = payload.get('role_date')

        current_id = item.get('_id') if item else 'Unknown'
        mgm_pk = item.get('mgmBldrgstPk', 'Unknown')

        try:
            if not item:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            # 서비스 레이어 접근
            service = location_raw_facade.address_service
            if source_type == 'group':
                building_service = building_facade.group_info_service
            elif source_type == 'basic':
                building_service = building_facade.basic_info_service
            else:
                building_service = building_facade.title_info_service

            keyword = item.get('newPlatPlc', '').strip()
            if not keyword:
                return {'success': False, 'id': current_id, 'error': 'Empty newPlatPlc'}

            # 동기화 파라미터 구성
            search_queries = [keyword]
            sync_params = {
                '_id': str(current_id),
                'search_queries': {'$in': search_queries},
                'updated_at': {'$gt': role_date},
                'mgmBldrgstPk': mgm_pk,
                'bldNm': item.get('bldNm')
            }

            # JGK 연동 및 검증 로직 실행 (이미 수정하신 AddressService.sync_from_jgk 호출)
            result = service.sync_from_jgk(sync_params, source=source_type)

            # 결과 반영
            if result.get('status') == 'success' and result.get('bdMgtSn'):
                item['bdMgtSn'] = result['bdMgtSn']
                item['dead'] = False  # 성공 시 dead 해제
            elif result.get('status') == 'fail' and result.get('dead'):
                item['dead'] = True
                item['bdMgtSn'] = None

            # 데이터 저장
            building_service.manager.driver('mongodb').store([item])

            return {'success': True, 'id': current_id}

        except Exception as e:
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            return {'success': False, 'id': current_id, 'error': error_detail, 'pk': mgm_pk}

    def sync_address_by_building_info(self, source_type: str, is_continue: bool = False, is_renew: bool = False):
        """건축물대장 기반 주소 마스터 동기화 로직 (Multi-Core)"""
        if source_type == 'group':
            building_service = building_facade.group_info_service
            msg_prefix = "🏢 [총괄표제부]"
        elif source_type == 'basic':
            building_service = building_facade.basic_info_service
            msg_prefix = "🏢 [기본개요]"
        else:
            building_service = building_facade.title_info_service
            msg_prefix = "🏠 [표제부]"

        self._send_slack(f"🚀 {msg_prefix} 멀티프로세싱 동기화 가동")

        try:
            per_page = 10000
            total_count = 0
            last_id = None
            service = location_raw_facade.address_service

            if is_continue:
                renew_threshold = 7 if is_renew else 9999
                last_point = self._get_last_sync_point(service, source_type, renew_threshold)
                if last_point and '_id' in last_point:
                    from bson import ObjectId
                    try:
                        last_id = ObjectId(last_point['_id'])
                    except:
                        last_id = last_point['_id']
                    self.message(f"🔄 {msg_prefix} 이어하기: {last_id} 이후부터 시작", fg='magenta')

            self.message(f"🏗️ [4-Core] {msg_prefix} 병렬 수집을 시작합니다.", fg='green')

            now = datetime.now()
            role_date = now - timedelta(days=7)

            with Pool(processes=4) as pool:
                while True:
                    query_params = {
                        'page': 1,
                        'per_page': per_page,
                        '$or': [
                            {'updated_at': {'$lt': role_date}},
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

                    # 워커에 전달할 페이로드 구성
                    worker_payloads = [
                        {'item': item, 'source_type': source_type, 'role_date': role_date}
                        for item in items
                    ]

                    # 병렬 처리 시작
                    results = pool.map(self._worker_sync_address_task, worker_payloads)

                    # 결과 집계 및 에러 출력
                    chunk_success_count = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') not in ['Empty newPlatPlc']:
                            self.message(f"❌ PK {r.get('pk')} 에러: {r['error']}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)

                    self.message(
                        f"  -> {msg_prefix} {total_count}건 처리 중... (성공: {chunk_success_count}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

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

        #self.sync_address_by_building_info('group', is_continue, is_renew)
        #self.sync_address_by_building_info('title', is_continue, is_renew)
        self.sync_address_by_building_info('basic', is_continue, is_renew)

        total_time = int(time.time() - start_time)
        self.message(f"✨ 전체 동기화 완료 (총 소요시간: {total_time}초)", fg='white', bg='blue')
        self._send_slack(f"✨ 주소 동기화 전체 완료 (소요시간: {total_time}초)")

    def handle_block_address(self, is_continue: bool = False, is_renew: bool = False):
        directory_path = f"{Config.get('app.project_root')}/resources/juso_go_kr/address_db/current"
        service = location_raw_facade.block_address_service

        self._send_slack("🏘️ 관련지번 마스터 임포트 가동")

        try:
            # 서비스 내부에서 read()를 통해 가져온 파일 목록
            files = service.get_import_target_files(directory_path)

            total_count = 0

            for file_path in files:
                file_name = os.path.basename(file_path)

                # 서비스 내부에서 read()를 통해 파싱하고 저장
                saved_count = service.import_single_file(file_path)

                total_count += saved_count
                self.message(f"  -> 📄 {file_name}: {saved_count}건 저장 완료", fg='white')

            self._send_slack(f"✨ 전체 임포트 종료 (총 {total_count}건)")

        except Exception as e:
            self._handle_error(e, "관련지번 임포트 중단")

    def handle_road_address(self, is_continue: bool = False, is_renew: bool = False):
        directory_path = f"{Config.get('app.project_root')}/resources/juso_go_kr/address_db/current"
        service = location_raw_facade.road_address_service

        self._send_slack("🏘️ 도로주소 마스터 임포트 가동")

        try:
            # 서비스 내부에서 read()를 통해 가져온 파일 목록
            files = service.get_import_target_files(directory_path)
            total_count = 0

            for file_path in files:
                file_name = os.path.basename(file_path)

                # 서비스 내부에서 read()를 통해 파싱하고 저장
                saved_count = service.import_single_file(file_path)

                total_count += saved_count
                self.message(f"  -> 📄 {file_name}: {saved_count}건 저장 완료", fg='white')

            self._send_slack(f"✨ 전체 임포트 종료 (총 {total_count}건)")

        except Exception as e:
            self._handle_error(e, "도로주소 임포트 중단")

    def handle_building_group(self, is_continue: bool = False, is_renew: bool = False):
        directory_path = f"{Config.get('app.project_root')}/resources/juso_go_kr/address_db/current"
        service = location_raw_facade.building_group_service

        self._send_slack("🏘️ 부가정보 마스터 임포트 가동")

        try:
            # 서비스 내부에서 read()를 통해 가져온 파일 목록
            files = service.get_import_target_files(directory_path)
            total_count = 0

            for file_path in files:
                file_name = os.path.basename(file_path)

                # 서비스 내부에서 read()를 통해 파싱하고 저장
                saved_count = service.import_single_file(file_path)

                total_count += saved_count
                self.message(f"  -> 📄 {file_name}: {saved_count}건 저장 완료", fg='white')

            self._send_slack(f"✨ 전체 임포트 종료 (총 {total_count}건)")

        except Exception as e:
            self._handle_error(e, "부가정보 임포트 중단")

    def handle_address_db(self):
        location_raw_facade.address_db_service.run()


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
        def sync_basic(is_continue, is_renew):
            self.sync_address_by_building_info('basic', is_continue, is_renew)

        @cli_group.command('location_raw:address_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_all_cmd(is_continue, is_renew):
            self.handle_sync_all(is_continue, is_renew)

        @cli_group.command('location_raw:block_address_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_block_address(is_continue, is_renew):
            self.handle_block_address(is_continue, is_renew)

        @cli_group.command('location_raw:road_address_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_road_address(is_continue, is_renew):
            self.handle_road_address(is_continue, is_renew)

        @cli_group.command('location_raw:building_group_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_building_group(is_continue, is_renew):
            self.handle_building_group(is_continue, is_renew)

        @cli_group.command('location_raw:address_db')
        def sync_address_db():
            self.handle_address_db()


__all__ = ['LocationRawCommand']