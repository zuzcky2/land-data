import click
from app.facade import command
from app.services.location.boundary import facade as boundary_facade
from app.features.contracts.command import AbstractCommand
from app.services.location.boundary.types.boundary import STATE, DISTRICT, TOWNSHIP, VILLAGE


class BoundaryCommand(AbstractCommand):

    def _process_sync_direct(self, location_type: str, label: str):
        """상위 데이터가 필요 없는 최상위 계층(STATE)을 위한 동기화 메서드"""
        try:
            command.message(f'🚀 [{label}] 직접 동기화를 시작합니다...', fg='green')

            per_page = 100
            # 서비스의 sync_from_vworld 사용 (단일 레이어 추출)
            meta = boundary_facade.service.sync_from_vworld(
                location_type=location_type,
                page=1,
                per_page=per_page
            )

            last_page = meta.last_page
            command.message(f'-> 총 {meta.total}건 ({last_page}페이지) 대상 확인', fg='cyan')

            if last_page > 1:
                for page in range(2, last_page + 1):
                    boundary_facade.service.sync_from_vworld(
                        location_type=location_type,
                        page=page,
                        per_page=per_page
                    )
                    command.message(f'   ... {page}/{last_page} 페이지 진행 중', fg='blue')

            command.message(f'✅ [{label}] 모든 데이터 쓰기 완료', fg='green')

        except Exception as e:
            self._handle_error(e, f"[{label}] 직접 Sync 실패 @see {__file__}")

    def _process_sync_hierarchy(self, parent_type: str, current_type: str, label: str):
        """상위 계층 데이터를 소스로 사용하는 계층적 동기화 메서드"""
        try:
            command.message(f'📂 [{label}] 계층적 동기화 시작 (Source: {parent_type.upper()})', fg='yellow')

            # 서비스에 새로 추가한 sync_hierarchy 호출
            total_count = boundary_facade.service.sync_hierarchy(
                parent_type=parent_type,
                current_type=current_type
            )

            command.message(f'✅ [{label}] 동기화 완료: 총 {total_count}개 데이터 저장', fg='green')

        except Exception as e:
            self._handle_error(e, f"[{label}] 계층 Sync 실패 @see {__file__}")

    def write_boundary_all(self):
        """
        모든 계층의 지역 정보를 VWorld에서 가져와 DB에 저장합니다.
        순서: State 직접 싱크 -> 상위 코드를 기반으로 하위 계층 동기화
        """
        try:
            # 1. 시도(State)는 부모가 없으므로 직접 싱크 (vworld -> mongodb)
            command.message('1. State 데이터를 동기화 중...', fg='green')
            boundary_facade.service.sync_from_vworld(location_type='state')

            # 2. 시군구(District) 동기화 (State 기반)
            command.message('2. District 데이터를 동기화 중...', fg='green')
            boundary_facade.service.sync_hierarchy(parent_type='state', current_type='district')

            # 3. 읍면동(Township) 동기화 (District 기반)
            command.message('3. Township 데이터를 동기화 중...', fg='green')
            boundary_facade.service.sync_hierarchy(parent_type='district', current_type='township')

            # 4. 리(Village) 동기화 (Township 기반)
            command.message('4. Village 데이터를 동기화 중...', fg='green')
            boundary_facade.service.sync_hierarchy(parent_type='township', current_type='village')

            command.message('모든 지역 경계 데이터 동기화 완료!', fg='blue')

        except Exception as e:
            command.message(f'실행에 실패하였습니다. @see {__file__}', fg='red')
            command.error_log(str(e))
            raise e

    def write_boundary_state(self):
        # 최상위 계층은 직접 싱크
        self._process_sync_direct(STATE, 'State')

    def write_boundary_district(self):
        # District는 State 데이터를 기반으로 싱크
        self._process_sync_hierarchy(STATE, DISTRICT, 'District')

    def write_boundary_township(self):
        # Township은 District 데이터를 기반으로 싱크
        self._process_sync_hierarchy(DISTRICT, TOWNSHIP, 'Township')

    def write_boundary_village(self):
        # Village는 Township 데이터를 기반으로 싱크
        self._process_sync_hierarchy(TOWNSHIP, VILLAGE, 'Village')

    def register_commands(self, cli_group):
        """CLI 그룹에 명령어 등록"""

        @cli_group.command('boundary_write:all')
        def boundary_write_all():
            self.write_boundary_all()

        @cli_group.command('boundary_write:state')
        def boundary_write_state():
            self.write_boundary_state()

        @cli_group.command('boundary_write:district')
        def boundary_write_district():
            self.write_boundary_district()

        @cli_group.command('boundary_write:township')
        def boundary_write_township():
            self.write_boundary_township()

        @cli_group.command('boundary_write:village')
        def boundary_write_village():
            self.write_boundary_village()


__all__ = ['BoundaryCommand']