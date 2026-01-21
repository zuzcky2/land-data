import click
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from multiprocessing import Pool
from app.services.location.raw import facade as location_raw_facade
from app.services.building.structure import facade as structure_facade

from app.features.contracts.command import AbstractCommand
from app.core.helpers.log import Log

class StructureBuildCommand(AbstractCommand):

    @staticmethod
    def _worker_address_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        """각 코어에서 독립적으로 실행될 빌드 태스크"""
        # 에러 추적을 위한 초기화
        current_id = item.get('_id') if item else 'Unknown'

        try:
            # item 자체가 None이거나 dict가 아닌 경우 방어
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            logger_name = f"{structure_facade.address_service.logger_name}_build"
            build_logger = Log.get_logger(logger_name)

            # 실제 빌드 서비스 호출
            result = structure_facade.address_service.build_by_address_raw(item)

            # 🚀 [수정 지점] result가 객체인지, 아니면 딕셔너리인지에 따라 안전하게 접근
            # 만약 result가 None이면 'NoneType' 에러 방지를 위해 방어 로직 강화
            if result:
                # result가 객체라면 getattr 사용, dict라면 .get() 사용
                address_id = getattr(result, 'building_manage_number', None)
                if address_id is None and isinstance(result, dict):
                    address_id = result.get('building_manage_number')

                item['address_id'] = address_id
                item['dead'] = False
            else:
                item['address_id'] = None
                item['dead'] = True

            if location_raw_facade and location_raw_facade.address_service:
                location_raw_facade.road_code_service.manager.driver('mongodb').store([{
                    'road_code_id': item['road_code_id'],
                    'address_id': item['address_id'],
                    'dead': item['dead']
                }])
            else:
                return {'success': False, 'id': current_id, 'error': 'Location service facade is None'}

            build_logger.info(f"Sync Start: {{'_id': '{str(current_id)}', 'bdMgtSn': '{item['address_id']}'}}")
            return {'success': True, 'id': current_id}

        except Exception as e:
            # 🚀 상세 에러 추적을 위해 에러 타입과 메시지를 함께 반환
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            return {'success': False, 'id': current_id, 'error': error_detail}

    def address_handle(self, is_continue: bool = False, is_renew: bool = False):
        """building_structure:address 명령어의 실제 구현부"""
        service = location_raw_facade.road_code_service
        page = 1
        per_page = 10000
        total_count = 0
        last_id = None

        self._send_slack("🏗️ 공간정보 결합 빌드 프로세스 가동")

        if is_continue:
            renew_threshold = 7 if is_renew else 9999
            last_point = self._get_last_sync_point(structure_facade.address_service, 'build', renew_threshold)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try: last_id = ObjectId(last_point['_id'])
                except: last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

        self.message("🏗️ [4-Core] 멀티프로세싱 공간정보 빌드를 시작합니다.", fg='green')

        # 수정된지 7일 지난것들만 작업
        now = datetime.now()
        role_date = now - timedelta(days=7)
        try:
            with Pool(processes=4) as pool:
                while True:
                    address_pagination = service.get_road_code_aggregate(page, per_page)

                    items = getattr(address_pagination, 'items', [])

                    if not items:
                        self.message("✅ 빌드 완료", fg='blue')
                        break

                    # 병렬 처리
                    results = pool.map(self._worker_address_build_task, items)

                    chunk_success_count = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') != 'No bdMgtSn':
                            self.message(f"❌ 에러 (ID: {r['id']}): {r['error']}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)
                    page = page + 1

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success_count}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ 전체 작업 종료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "공간정보 빌드 프로세스 중단")

    @staticmethod
    def _worker_complex_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        """각 코어에서 독립적으로 실행될 빌드 태스크"""
        # 에러 추적을 위한 초기화
        current_id = item.get('_id') if item else 'Unknown'

        try:
            # item 자체가 None이거나 dict가 아닌 경우 방어
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            logger_name = f"{structure_facade.complex_service.logger_name}_build"
            build_logger = Log.get_logger(logger_name)

            building_manage_number = item.get('building_manage_number')
            if not building_manage_number:
                return {'success': False, 'id': current_id, 'error': 'No building_manage_number'}

            # 실제 빌드 서비스 호출
            structure_facade.complex_service.build_by_address(item)

            if location_raw_facade and location_raw_facade.address_service:
                location_raw_facade.address_service.manager.driver('mongodb').store([item])
            else:
                return {'success': False, 'id': current_id, 'error': 'Location service facade is None'}

            build_logger.info(f"Sync Start: {{'_id': '{str(current_id)}', 'building_manage_number': '{building_manage_number}'}}")
            return {'success': True, 'id': current_id}

        except Exception as e:
            # 🚀 상세 에러 추적을 위해 에러 타입과 메시지를 함께 반환
            import traceback
            error_detail = f"{str(e)}\n{traceback.format_exc()}"
            return {'success': False, 'id': current_id, 'error': error_detail}

    def complex_handle(self, is_continue: bool = False, is_renew: bool = False):
        """building_structure:complex 명령어의 실제 구현부"""
        service = structure_facade.address_service
        per_page = 10000
        total_count = 0
        last_id = None

        self._send_slack("🏗️ 단지정보 빌드 프로세스 가동")

        if is_continue:
            renew_threshold = 7 if is_renew else 9999
            last_point = self._get_last_sync_point(structure_facade.complex_service, 'build', renew_threshold)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try: last_id = ObjectId(last_point['_id'])
                except: last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

        self.message("🏗️ [4-Core] 멀티프로세싱 단지정보 빌드를 시작합니다.", fg='green')

        # 수정된지 7일 지난것들만 작업
        now = datetime.now()
        role_date = now - timedelta(days=7)
        try:
            with Pool(processes=4) as pool:
                while True:
                    query_params = {
                        'page': 1,
                        'per_page': per_page,
                        'sort': [('_id', 1)]
                    }
                    if last_id:
                        query_params['_id'] = {'$gt': last_id}

                    address_pagination = service.get_list(query_params)

                    items = getattr(address_pagination, 'items', [])

                    if not items:
                        self.message("✅ 빌드 완료", fg='blue')
                        break

                    # 병렬 처리
                    results = pool.map(self._worker_complex_build_task, items)

                    chunk_success_count = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') != 'No building_manage_number':
                            self.message(f"❌ 에러 (ID: {r['id']}): {r['error']}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success_count}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ 전체 작업 종료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "단지정보 빌드 프로세스 중단")

    def register_commands(self, cli_group):
        @cli_group.command('building_structure:address', help='수집된 주소 기반 공간정보 결합')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def build_address_cmd(is_continue, is_renew):
            self.address_handle(is_continue, is_renew)

        @cli_group.command('building_structure:complex', help='주소 공간정보 기반 단지정보 생성')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def build_address_cmd(is_continue, is_renew):
            self.complex_handle(is_continue, is_renew)

__all__=['StructureBuildCommand']