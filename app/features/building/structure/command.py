import click
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from multiprocessing import Pool
from app.services.building.raw import facade as building_raw_facade
from app.services.building.structure import facade as structure_facade

from app.features.contracts.command import AbstractCommand
from app.core.helpers.log import Log


class StructureBuildCommand(AbstractCommand):

    # ──────────────────────────────── ADDRESS ────────────────────────────────

    @staticmethod
    def _worker_address_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            bd_mgt_sn = item.get('bdMgtSn')
            if not bd_mgt_sn:
                return {'success': False, 'id': current_id, 'error': 'No bdMgtSn'}

            build_logger = Log.get_logger(f"{structure_facade.address_service.logger_name}_build")
            structure_facade.address_service.build_by_building_raw(item)

            build_logger.info(f"Built address for bdMgtSn: {bd_mgt_sn}")
            return {'success': True, 'id': current_id}

        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def address_handle(self, is_continue: bool = False, is_renew: bool = False):
        per_page = 5000
        total_count = 0

        self._send_slack("🏗️ 주소 빌드 프로세스 가동 (building_raw 기반)")
        self.message("🏗️ [4-Core] 멀티프로세싱 주소 빌드를 시작합니다.", fg='green')

        sources = [
            (building_raw_facade.group_info_service, {}, '총괄표제부'),
            (building_raw_facade.title_info_service, {'regstrGbCd': '1'}, '일반건축물'),
        ]

        try:
            with Pool(processes=4) as pool:
                for service, base_filter, source_name in sources:
                    page = 1
                    self.message(f"\n📦 [{source_name}] 빌드 시작", fg='cyan')

                    while True:
                        params = {**base_filter, 'page': page, 'per_page': per_page}
                        pagination = service.get_list(params)
                        items = getattr(pagination, 'items', [])

                        if not items:
                            self.message(f"  ✅ [{source_name}] 완료", fg='blue')
                            break

                        results = pool.map(self._worker_address_build_task, items)

                        chunk_success = sum(1 for r in results if r['success'])
                        for r in results:
                            if not r['success'] and r.get('error') not in ('No bdMgtSn',):
                                self.message(f"  ❌ (ID: {r['id']}): {r['error'][:120]}", fg='red')

                        total_count += len(items)
                        page += 1
                        self.message(
                            f"  -> {total_count}건 처리 중... (성공: {chunk_success}/{len(items)}, 페이지: {page-1})",
                            fg='white'
                        )

                        if len(items) < per_page:
                            break

            self.message(f"✨ 전체 작업 종료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 주소 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "주소 빌드 프로세스 중단")

    def address_update_handle(self):
        per_page = 5000
        page = 1
        total_count = 0

        self._send_slack("🔄 geo_point 없는 주소 재빌드 프로세스 가동")
        self.message("🔄 geo_point 없는 주소 재빌드를 시작합니다.", fg='green')

        try:
            with Pool(processes=4) as pool:
                while True:
                    addr_pagination = structure_facade.address_service.get_list({
                        'geo_point': None,
                        'building_manage_number': {'$ne': None},
                        'page': page,
                        'per_page': per_page,
                        'sort': [('_id', 1)]
                    })
                    addr_items = getattr(addr_pagination, 'items', [])

                    if not addr_items:
                        self.message("✅ 재빌드 완료", fg='blue')
                        break

                    bd_mgt_sns = [a['building_manage_number'] for a in addr_items if a.get('building_manage_number')]

                    raw_items = []
                    for bdMgtSn in bd_mgt_sns:
                        raw = building_raw_facade.group_info_service.get_detail({'bdMgtSn': bdMgtSn})
                        if not raw:
                            raw = building_raw_facade.title_info_service.get_detail({'bdMgtSn': bdMgtSn, 'regstrGbCd': '1'})
                        if raw:
                            raw_items.append(raw)

                    if not raw_items:
                        page += 1
                        continue

                    results = pool.map(self._worker_address_build_task, raw_items)
                    chunk_success = sum(1 for r in results if r['success'])
                    total_count += len(raw_items)
                    page += 1

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success}/{len(raw_items)})",
                        fg='white'
                    )

                    if len(addr_items) < per_page:
                        break

            self.message(f"✨ 재빌드 완료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ geo_point 재빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "주소 재빌드 프로세스 중단")

    # ──────────────────────────────── COMPLEX ────────────────────────────────

    @staticmethod
    def _worker_complex_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            building_manage_number = item.get('building_manage_number')
            if not building_manage_number:
                return {'success': False, 'id': current_id, 'error': 'No building_manage_number'}

            structure_facade.complex_service.build_by_address(item)
            return {'success': True, 'id': current_id}

        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def complex_handle(self, is_continue: bool = False, is_renew: bool = False):
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
                try:
                    last_id = ObjectId(last_point['_id'])
                except Exception:
                    last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

        self.message("🏗️ [4-Core] 멀티프로세싱 단지정보 빌드를 시작합니다.", fg='green')

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

    # ──────────────────────────────── BUILDING ───────────────────────────────

    @staticmethod
    def _worker_building_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            mgm_pk = item.get('mgmBldrgstPk')
            if not mgm_pk:
                return {'success': False, 'id': current_id, 'error': 'No mgmBldrgstPk'}

            structure_facade.building_service.build_by_title_info(item)
            return {'success': True, 'id': current_id}

        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def building_handle(self, is_continue: bool = False):
        """title_info(표제부, regstrKindCd=3) 기반 buildings 컬렉션 빌드."""
        per_page = 5000
        total_count = 0
        last_id = None

        self._send_slack("🏗️ 건물(동) 빌드 프로세스 가동")
        self.message("🏗️ [4-Core] 건물(동) 빌드를 시작합니다.", fg='green')

        if is_continue:
            last_point = self._get_last_sync_point(structure_facade.building_service, 'build', 9999)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try:
                    last_id = ObjectId(last_point['_id'])
                except Exception:
                    last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

        try:
            with Pool(processes=4) as pool:
                while True:
                    query_params = {
                        'regstrKindCd': '3',
                        'page': 1,
                        'per_page': per_page,
                        'sort': [('_id', 1)]
                    }
                    if last_id:
                        query_params['_id'] = {'$gt': last_id}

                    pagination = building_raw_facade.title_info_service.get_list(query_params)
                    items = getattr(pagination, 'items', [])

                    if not items:
                        self.message("✅ 빌드 완료", fg='blue')
                        break

                    results = pool.map(self._worker_building_build_task, items)

                    chunk_success = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') != 'No mgmBldrgstPk':
                            self.message(f"❌ 에러 (ID: {r['id']}): {r['error'][:120]}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ 건물 빌드 완료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 건물 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "건물 빌드 프로세스 중단")

    # ──────────────────────────────── FLOOR ──────────────────────────────────

    @staticmethod
    def _worker_floor_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            mgm_pk = item.get('mgmBldrgstPk')
            if not mgm_pk:
                return {'success': False, 'id': current_id, 'error': 'No mgmBldrgstPk'}

            structure_facade.floor_service.build_by_floor_info(item)
            return {'success': True, 'id': current_id}

        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def floor_handle(self, is_continue: bool = False):
        """floor_info 기반 floors 컬렉션 빌드."""
        per_page = 5000
        total_count = 0
        last_id = None

        self._send_slack("🏗️ 층 정보 빌드 프로세스 가동")
        self.message("🏗️ [4-Core] 층 정보 빌드를 시작합니다.", fg='green')

        if is_continue:
            last_point = self._get_last_sync_point(structure_facade.floor_service, 'build', 9999)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try:
                    last_id = ObjectId(last_point['_id'])
                except Exception:
                    last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

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

                    pagination = building_raw_facade.floor_info_service.get_list(query_params)
                    items = getattr(pagination, 'items', [])

                    if not items:
                        self.message("✅ 층 빌드 완료", fg='blue')
                        break

                    results = pool.map(self._worker_floor_build_task, items)

                    chunk_success = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') != 'No mgmBldrgstPk':
                            self.message(f"❌ 에러 (ID: {r['id']}): {r['error'][:120]}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ 층 빌드 완료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 층 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "층 빌드 프로세스 중단")

    # ──────────────────────────────── UNIT ───────────────────────────────────

    @staticmethod
    def _worker_unit_build_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}

            mgm_pk = item.get('mgmBldrgstPk')
            if not mgm_pk:
                return {'success': False, 'id': current_id, 'error': 'No mgmBldrgstPk'}

            structure_facade.unit_service.build_by_basic_info(item)
            return {'success': True, 'id': current_id}

        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def unit_handle(self, is_continue: bool = False):
        """basic_info(전유부, regstrKindCd=4) 기반 units 컬렉션 빌드."""
        per_page = 5000
        total_count = 0
        last_id = None

        self._send_slack("🏗️ 호실 빌드 프로세스 가동")
        self.message("🏗️ [4-Core] 호실 빌드를 시작합니다.", fg='green')

        if is_continue:
            last_point = self._get_last_sync_point(structure_facade.unit_service, 'build', 9999)
            if last_point and '_id' in last_point:
                from bson import ObjectId
                try:
                    last_id = ObjectId(last_point['_id'])
                except Exception:
                    last_id = last_point['_id']
                self.message(f"🔄 이어하기: {last_id}부터 시작", fg='magenta')

        try:
            with Pool(processes=4) as pool:
                while True:
                    query_params = {
                        'regstrKindCd': '4',
                        'page': 1,
                        'per_page': per_page,
                        'sort': [('_id', 1)]
                    }
                    if last_id:
                        query_params['_id'] = {'$gt': last_id}

                    pagination = building_raw_facade.basic_info_service.get_list(query_params)
                    items = getattr(pagination, 'items', [])

                    if not items:
                        self.message("✅ 호실 빌드 완료", fg='blue')
                        break

                    results = pool.map(self._worker_unit_build_task, items)

                    chunk_success = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success'] and r.get('error') != 'No mgmBldrgstPk':
                            self.message(f"❌ 에러 (ID: {r['id']}): {r['error'][:120]}", fg='red')

                    last_item = items[-1]
                    last_id = last_item['_id']
                    total_count += len(items)

                    self.message(
                        f"  -> {total_count}건 처리 중... (성공: {chunk_success}/{len(items)}, ID: {last_id})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ 호실 빌드 완료 (총 {total_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ 호실 빌드 완료 (총 {total_count}건 처리)")

        except Exception as e:
            self._handle_error(e, "호실 빌드 프로세스 중단")

    # ──────────────────────────────── KAPT SYNC ──────────────────────────────

    @staticmethod
    def _worker_kapt_sync_task(item: Dict[str, Any]) -> Dict[str, Any]:
        current_id = item.get('_id') if item else 'Unknown'
        try:
            if item is None:
                return {'success': False, 'id': 'None', 'error': 'Item is None'}
            kapt_code = item.get('kaptCode')
            if not kapt_code:
                return {'success': False, 'id': current_id, 'error': 'No kaptCode'}
            matched = structure_facade.complex_service.sync_kapt(item)
            return {'success': True, 'id': current_id, 'matched': matched}
        except Exception as e:
            import traceback
            return {'success': False, 'id': current_id, 'error': f"{str(e)}\n{traceback.format_exc()}"}

    def kapt_sync_handle(self):
        """K-APT 단지 정보를 complexes에 병합합니다."""
        per_page = 1000
        total_count = 0
        matched_count = 0

        self._send_slack("🔗 K-APT 단지 정보 complexes 병합 시작")
        self.message("🔗 K-APT → complexes 병합을 시작합니다.", fg='green')

        try:
            with Pool(processes=4) as pool:
                page = 1
                while True:
                    pagination = building_raw_facade.kapt_basic_service.get_list({
                        'page': page, 'per_page': per_page
                    })
                    items = getattr(pagination, 'items', [])

                    if not items:
                        self.message("✅ K-APT 병합 완료", fg='blue')
                        break

                    results = pool.map(self._worker_kapt_sync_task, items)

                    chunk_matched = sum(1 for r in results if r.get('matched'))
                    chunk_success = sum(1 for r in results if r['success'])
                    for r in results:
                        if not r['success']:
                            self.message(f"❌ (ID: {r['id']}): {r['error'][:100]}", fg='red')

                    total_count += len(items)
                    matched_count += chunk_matched
                    page += 1

                    self.message(
                        f"  -> {total_count}건 처리 (매칭: {matched_count}, 페이지: {page-1})",
                        fg='white'
                    )

                    if len(items) < per_page:
                        break

            self.message(f"✨ K-APT 병합 완료 (총 {total_count}건, 매칭 {matched_count}건)", fg='blue', bg='white')
            self._send_slack(f"✨ K-APT 병합 완료 ({matched_count}/{total_count} 매칭)")

        except Exception as e:
            self._handle_error(e, "K-APT 병합 프로세스 중단")

    # ──────────────────────────────── REGISTER ───────────────────────────────

    def register_commands(self, cli_group):

        @cli_group.command('building_structure:address', help='수집된 주소 기반 공간정보 결합')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def build_address_cmd(is_continue, is_renew):
            self.address_handle(is_continue, is_renew)

        @cli_group.command('building_structure:address-update', help='geo_point 없는 주소 재빌드')
        def build_address_update_cmd():
            self.address_update_handle()

        @cli_group.command('building_structure:complex', help='주소 공간정보 기반 단지정보 생성')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def build_complex_cmd(is_continue, is_renew):
            self.complex_handle(is_continue, is_renew)

        @cli_group.command('building_structure:building', help='표제부 기반 건물(동) 정보 생성')
        @click.option('--continue', 'is_continue', is_flag=True)
        def build_building_cmd(is_continue):
            self.building_handle(is_continue)

        @cli_group.command('building_structure:floor', help='층정보 기반 floors 컬렉션 생성')
        @click.option('--continue', 'is_continue', is_flag=True)
        def build_floor_cmd(is_continue):
            self.floor_handle(is_continue)

        @cli_group.command('building_structure:unit', help='전유부 기반 호실 정보 생성')
        @click.option('--continue', 'is_continue', is_flag=True)
        def build_unit_cmd(is_continue):
            self.unit_handle(is_continue)

        @cli_group.command('building_structure:kapt-sync', help='K-APT 단지 정보를 complexes에 병합')
        def kapt_sync_cmd():
            self.kapt_sync_handle()


__all__ = ['StructureBuildCommand']
