import ast
import os
import re
import click
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from app.facade import command
from app.services.location.raw import facade as address_facade
from app.services.location.boundary import facade as boundary_facade
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

            # 서비스 기본 로거 이름 뒤에 소스 타입을 붙여서 로그 파일 식별 (예: building_raw_group)
            full_logger_name = f"{service.logger_name}_{source_type}"
            logger_config = Config.get(f'logging.{full_logger_name}')

            if not logger_config:
                logger_config = Config.get(f'logging.{service.logger_name}')

            log_path = Env.get('LOG_PATH', '/var/volumes/log')
            log_filename = os.path.join(log_path, logger_config['filename'])

            if not os.path.exists(log_filename):
                return None

            with open(log_filename, 'r', encoding='utf-8') as f:
                # 마지막 100줄을 읽어 역순 탐색
                lines = f.readlines()[-100:]
                for line in reversed(lines):
                    if "Sync Start: " in line:
                        # 타임스탬프 파싱 및 갱신 주기 확인
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
        """실제 주소 동기화 로직"""
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
            # Cursor 기반: 항상 page=1
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

                    # 소스별 로깅을 위해 source 인자 전달
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

        # 1. 총괄표제부
        self.sync_address_by_building_info('group', is_continue, is_renew)

        # 2. 표제부
        self.sync_address_by_building_info('title', is_continue, is_renew)

        total_time = int(time.time() - start_time)
        command.message(f"✨ 전체 동기화 완료 (총 소요시간: {total_time}초)", fg='white', bg='blue')

    def handle_build_address(self, is_continue: bool = False, is_renew: bool = False):
        """
        수집된 주소 마스터를 바탕으로 좌표 및 공간정보를 결합(Build)합니다.
        로그 기반 이어하기 및 30일 갱신 로직이 포함되어 있습니다.
        """
        service = address_facade.address_service
        per_page = 1000
        total_count = 0
        last_id = None

        # 1. 이어하기 지점 파악 (build 전용 로그 소스 사용)
        if is_continue:
            # 갱신 주기: is_renew가 True면 30일, 아니면 무제한(9999)
            renew_threshold = 30 if is_renew else 9999
            # build_address 작업은 'build'라는 별도 소스로 로그를 관리한다고 가정
            last_point = self._get_last_sync_point(service, 'build', renew_threshold)

            if last_point and '_id' in last_point:
                from bson import ObjectId
                try:
                    last_id = ObjectId(last_point['_id'])
                except:
                    last_id = last_point['_id']
                command.message(f"🔄 빌드 이어하기: {last_id} 이후부터 시작합니다.", fg='magenta')

        # 2. 행정구역 BBOX 캐시 (API 호출 최소화)
        boundary_cache = {}
        command.message("🏗️ 주소 기반 공간정보 빌드 작업을 시작합니다.", fg='green')

        # 로그 기록을 위한 커스텀 로거 가져오기
        build_logger = Log.get_logger(f"{service.logger_name}_build")

        while True:
            # Cursor 방식: 항상 page=1
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
                command.message("✅ 모든 주소에 대한 빌드 작업을 마쳤습니다.", fg='blue')
                break

            for item in items:
                try:
                    # 로그 기록 (Sync Start 형식을 맞춰야 _get_last_sync_point가 읽을 수 있음)
                    build_logger.info(
                        f"Sync Start: {{'_id': '{str(item['_id'])}', 'bdMgtSn': '{item.get('bdMgtSn')}'}}")

                    bd_mgt_sn = item.get('bdMgtSn')
                    if not bd_mgt_sn:
                        last_id = item['_id']
                        continue

                    # 3. 행정구역 BBOX 캐싱
                    adm_cd_5 = bd_mgt_sn[:5]
                    if adm_cd_5 not in boundary_cache:
                        boundary = boundary_facade.service.get_boundary(
                            {'item_code': adm_cd_5, 'use_polygon': False})
                        boundary_cache[adm_cd_5] = boundary.bbox if boundary else None

                    bbox = boundary_cache[adm_cd_5]

                    # 4. 주소 쿼리 생성 (도로명 + 본번 + 부번)
                    road_query = f"{item.get('rn', '')} {item.get('buldMnnm', '')}"
                    if item.get('buldSlno') and str(item['buldSlno']).strip() not in ['', '0']:
                        road_query += f"-{item['buldSlno']}"

                    # 5. 좌표(Point) 수집 Chain 호출
                    point_pagination = address_facade.point_geometry_service.get_list_by_chain({
                        'pnu': bd_mgt_sn[:19],
                        'bdMgtSn': bd_mgt_sn,
                        'query': road_query,
                        'bbox': bbox,
                        'page': 1,
                        'per_page': 1000
                    })

                    # 6. 지적도(Continuous) 수집 및 포인트 보정
                    for point_item in getattr(point_pagination, 'items', []):
                        point = point_item.get('point', {})
                        if not point.get('x') or not point.get('y'):
                            continue

                        continuous = address_facade.continuous_geometry_service.get_detail_by_chain({
                            'id': point_item.get('continuous_id'),
                            'bdMgtSn': bd_mgt_sn,
                            'latitude': float(point['x']),
                            'longitude': float(point['y'])
                        })

                        if continuous and 'id' in continuous and not point_item.get('continuous_id'):
                            point_item['continuous_id'] = continuous['id']
                            address_facade.point_geometry_service.manager.mongodb_driver.store([point_item])

                    # 7. 상태 갱신
                    last_id = item['_id']
                    total_count += 1
                    if total_count % 100 == 0:
                        command.message(f"  -> {total_count}건 공간정보 결합 중... (현재 ID: {last_id})", fg='white')

                except Exception as e:
                    command.message(f"⚠️ 에러 (ID: {item.get('_id')}): {e}", fg='red')
                    last_id = item['_id']
                    continue

            if len(items) < per_page:
                break

            time.sleep(0.05)

        command.message(f"🎉 빌드 완료! 총 {total_count}건 처리됨.", fg='blue')

    def register_commands(self, cli_group):
        """CLI 명령어 등록"""

        @cli_group.command('location_address:sync_by_group')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_group(is_continue, is_renew):
            self.sync_address_by_building_info('group', is_continue, is_renew)

        @cli_group.command('location_address:sync_by_title')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_title(is_continue, is_renew):
            self.sync_address_by_building_info('title', is_continue, is_renew)

        @cli_group.command('location_address:sync_all')
        @click.option('--continue', 'is_continue', is_flag=True)
        @click.option('--renew', 'is_renew', is_flag=True)
        def sync_all_cmd(is_continue, is_renew):
            self.handle_sync_all(is_continue, is_renew)

        @cli_group.command('address:build', help='수집된 주소 기반 공간정보 결합')
        @click.option('--continue', 'is_continue', is_flag=True, help='마지막 지점부터 이어서 빌드합니다.')
        @click.option('--renew', 'is_renew', is_flag=True, help='30일 이상된 로그면 처음부터 빌드합니다.')
        def build_address_cmd(is_continue, is_renew):
            # 🚀 self를 통해 클래스 메서드를 호출해야 합니다.
            self.handle_build_address(is_continue, is_renew)



__all__ = ['LocationAddressCommand']