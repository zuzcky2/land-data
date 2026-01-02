# app/features/building/raw/command.py

import click
from app.facade import command
from app.services.building.raw import facade as raw_facade
from app.services.building.raw.services.abstract_service import AbstractService
from app.services.location.boundary import facade as boundary_facade
from app.features.contracts.command import AbstractCommand


class BuildingRawCommand(AbstractCommand):

    def sync_building_registers_by_township(self, service: AbstractService):
        """
        DB에 저장된 모든 법정동(Township) 목록을 끝까지 순회하며 갱신합니다.
        """
        try:
            current_township_page = 1
            per_page = 100
            total_synced_townships = 0

            command.message('🚀 전국의 모든 법정동 순회 및 건축물대장 수집을 시작합니다.', fg='green')

            while True:
                # 1. 법정동 목록 조회
                township_pagination = boundary_facade.service.get_boundaries(
                    params={
                        'location_type': 'township',
                        'page': current_township_page,
                        'per_page': per_page
                    },
                    driver_name='mongodb'
                )

                items = getattr(township_pagination, 'items', [])

                # 가져온 아이템이 없으면 완전히 종료
                if not items:
                    command.message(f"--- 더 이상 가져올 법정동 데이터가 없습니다. (Page: {current_township_page}) ---", fg='yellow')
                    break

                for township in items:
                    full_code = township.item_code
                    sigungu_cd = full_code[:5]
                    bjdong_cd = f"{full_code[5:8]}00"

                    command.message(f"📦 [{township.item_full_name}] 수집 시작...", fg='cyan')

                    # 해당 법정동의 모든 페이지 수집 (이미 검증된 로직)
                    self._sync_all_pages_for_township(service, sigungu_cd, bjdong_cd)
                    total_synced_townships += 1

                # [수정포인트] totalCount나 last_page를 믿지 않고, 가져온 개수로 판단
                items_count = len(items)
                command.message(f"--- 법정동 목록 {current_township_page} 페이지 완료 ({items_count}개 처리) ---", fg='yellow')

                # 가져온 개수가 per_page(100)보다 적으면 마지막 페이지임
                if items_count < per_page:
                    break

                # 100개를 꽉 채워서 가져왔다면 다음 페이지가 더 있다고 가정하고 이동
                current_township_page += 1

            command.message(f'✅ 전체 {total_synced_townships}개 법정동 수집 대장정 완료!', fg='blue')

        except Exception as e:
            self._handle_error(e, f"일괄 수집 프로세스 중단 @see {__file__}")

    def _sync_all_pages_for_township(self, service: AbstractService, sigungu_cd: str, bjdong_cd: str):
        """특정 법정동의 데이터를 마지막 페이지까지 강제로 순회하며 가져옵니다."""
        current_page = 1
        per_page = 100

        while True:
            # 서비스 호출
            sync_result = service.sync_from_dgk({
                'sigunguCd': sigungu_cd,
                'bjdongCd': bjdong_cd,
                'page': current_page,
                'per_page': per_page
            })

            items_count = sync_result.get('count', 0)
            total_items = sync_result.get('total', 0)

            # [디버깅] 실제 넘어오는 total 값을 확인해봅니다.
            # 만약 여기서 total이 100 이하로 찍힌다면 드라이버의 _get_total_count 문제입니다.
            # command.message(f"      DEBUG: total={total_items}, count={items_count}", fg='black')

            if items_count > 0:
                command.message(f"  -> {current_page}p: {items_count}건 완료", fg='white')

            # [수정된 탈출 조건]
            # 1. 가져온 데이터가 아예 없으면 종료
            if items_count == 0:
                break

            # 2. 이번에 가져온 데이터가 요청한 100건보다 적으면 종료 (마지막 페이지 확신)
            if items_count < per_page:
                break

            # 3. 만약 API가 계속 100건을 준다면, 안전장치로 100페이지(1만건)까지만 시도
            if current_page >= 100:
                break

            # [핵심] 페이지 증가
            current_page += 1

            # API 과부하 방지
            import time
            time.sleep(0.1)

    def register_commands(self, cli_group):
        """CLI 그룹에 명령어 등록"""

        @cli_group.command('building_raw:title_info')
        def sync_title_info():
            """[배치] 모든 법정동의 건축물대장 표제부를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.title_info_service)

        @cli_group.command('building_raw:basic_info')
        def sync_basic_info():
            """[배치] 모든 법정동의 건축물대장 기본정보를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.basic_info_service)

        @cli_group.command('building_raw:floor_info')
        def sync_floor_info():
            """[배치] 모든 법정동의 건축물대장 층정보를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.floor_info_service)

        @cli_group.command('building_raw:area_info')
        def sync_area_info():
            """[배치] 모든 법정동의 건축물대장 면적정보를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.area_info_service)

        @cli_group.command('building_raw:price_info')
        def sync_price_info():
            """[배치] 모든 법정동의 건축물대장 가격정보를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.price_info_service)

        @cli_group.command('building_raw:address_info')
        def sync_address_info():
            """[배치] 모든 법정동의 건축물대장 주소정보를 순회하며 갱신합니다."""
            self.sync_building_registers_by_township(raw_facade.address_info_service)

        @cli_group.command('building_raw:all')
        def sync_all():
            self.sync_building_registers_by_township(raw_facade.title_info_service)
            self.sync_building_registers_by_township(raw_facade.basic_info_service)
            self.sync_building_registers_by_township(raw_facade.floor_info_service)
            self.sync_building_registers_by_township(raw_facade.area_info_service)
            self.sync_building_registers_by_township(raw_facade.price_info_service)
            self.sync_building_registers_by_township(raw_facade.address_info_service)



__all__ = ['BuildingRawCommand']