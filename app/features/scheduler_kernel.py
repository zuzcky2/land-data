"""스케줄러 커널 모듈

애플리케이션의 모든 백그라운드 작업을 등록하고 관리하는 중앙 집중식 스케줄러입니다.
MongoDB JobStore 사용을 위해 모든 작업 함수는 최상위 레벨에 정의되어야 합니다.
"""

from typing import Optional, Callable, Dict, List, Union, Any
import logging
from dataclasses import dataclass
from pytz import timezone
import datetime

from app.facade import scheduler
from app.core.helpers.env import Env
from app.core.helpers.log import Log
from app.services.message.webhook import facade as webhook_facade

# 스케줄러 전용 로거
logger: logging.Logger = Log.get_logger('scheduler')

# 기본 타임존 설정 (한국 시간)
KST_TIMEZONE = timezone('Asia/Seoul')


# --- 🚀 알림 및 실행 유틸리티 ---

def send_scheduler_slack(status: str, job_name: str, error: str = None):
    """스케줄러 실행 상태를 슬랙으로 전송"""
    try:
        emoji = "🏃" if status == "START" else "✅" if status == "SUCCESS" else "🔥"
        msg = f"{emoji} *[Scheduler]* {job_name} 작업 {status}"
        if error:
            msg += f"\n> ❌ *Error Detail*: {error}"

        webhook_facade.slack_service.send_message('scheduler', [msg])
    except Exception as e:
        logger.error(f"슬랙 알림 전송 실패: {e}")

def execute_job(job_func: Callable, job_name: str, **kwargs):
    """작업 실행 및 알림 공통 래퍼"""
    send_scheduler_slack("START", job_name)
    try:
        job_func(**kwargs)
        send_scheduler_slack("SUCCESS", job_name)
    except Exception as e:
        logger.error(f"❌ 작업 실행 중 에러 발생 [{job_name}]: {e}")
        send_scheduler_slack("FAILURE", job_name, error=str(e))
        raise e


# --- 🚀 스케줄러 실행을 위한 전역 래퍼 함수 (Top-level Functions) ---

# --- K-APT 관련 래퍼 함수 ---
def job_building_raw_kapt_list():
    """K-APT 단지 목록 수집 (00:00)"""
    from app.features.building.raw.command import BuildingRawCommand
    execute_job(BuildingRawCommand().handle_kapt_list, "K-APT 단지 목록 수집", is_continue=True, is_renew=True)

def job_building_raw_kapt_basic():
    """K-APT 기본정보 수집 (01:00)"""
    from app.features.building.raw.command import BuildingRawCommand
    from app.services.building.raw import facade as raw_facade
    execute_job(BuildingRawCommand().handle_kapt_children, "K-APT 단지 기본정보 수집",
                is_continue=True, is_renew=True, service=raw_facade.kapt_basic_service)

def job_building_raw_kapt_detail():
    """K-APT 상세정보 수집 (02:00)"""
    from app.features.building.raw.command import BuildingRawCommand
    from app.services.building.raw import facade as raw_facade
    execute_job(BuildingRawCommand().handle_kapt_children, "K-APT 단지 상세정보 수집",
                is_continue=True, is_renew=True, service=raw_facade.kapt_detail_service)

# --- 기존 주소/건축물 래퍼 함수 ---
def job_location_raw_address_db():
    """주소DB 전체분 다운로드 및 압축해제 (00:00)"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_address_db, "도로명주소 원천 DB 다운로드 및 갱신")

def job_location_raw_road_address_sync():
    """도로명주소 마스터 임포트 (01:00)"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_road_address, "도로명주소(건물) 마스터 데이터 임포트")

def job_location_raw_block_address_sync():
    """관련지번 마스터 임포트 (02:00)"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_block_address, "관련지번 마스터 데이터 임포트")

def job_location_raw_building_group_sync():
    """부가정보(건물군) 마스터 임포트 (03:00)"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_building_group, "주소 부가정보 마스터 데이터 임포트")

def job_location_raw_road_code_sync():
    """도로명 코드 마스터 임포트 (00:30)"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_road_code, "도로명 코드 마스터 데이터 임포트")

def job_boundary_update():
    """지역 경계 데이터 업데이트 (00:00)"""
    from app.features.location.boundary.command import BoundaryCommand
    execute_job(BoundaryCommand().write_boundary_all, "지역경계 데이터 일일 업데이트")

def job_building_raw_sync():
    """건축물대장 원천 데이터 동기화 (01:00)"""
    from app.features.building.raw.command import BuildingRawCommand
    execute_job(BuildingRawCommand().handle_sync_all, "건축물대장 전체 정보 일괄 수집", is_continue=True, is_renew=True)

def job_building_structure_address_build():
    """공간정보 빌드 (03:00)"""
    from app.features.building.structure.command import StructureBuildCommand
    execute_job(StructureBuildCommand().address_handle, "주소 기반 좌표 및 지적도 결합 빌드", is_continue=False, is_renew=False)


@dataclass
class ScheduleConfig:
    # ... (데이터 클래스 내용 유지) ...
    func: Callable
    trigger: str
    job_id: str
    name: str
    hour: Optional[Union[int, str]] = None
    minute: Optional[Union[int, str]] = None
    day: Optional[Union[int, str]] = None
    day_of_week: Optional[str] = None
    misfire_grace_time: int = 300
    max_instances: int = 1
    coalesce: bool = False
    environments: List[str] = None

    def __post_init__(self):
        if self.environments is None:
            self.environments = ['local', 'development', 'production']


class SchedulerRegistry:
    # ... (생략: __init__, register 메서드 동일) ...
    def __init__(self):
        self.schedules: List[ScheduleConfig] = []
        self.current_env = Env.get('APP_ENV', 'local')

    def register(self, config: ScheduleConfig) -> None:
        if self.current_env not in config.environments:
            logger.debug(f"스케줄 건너뜀: {config.name} (환경 미일치)")
            return
        try:
            trigger_kwargs = {'timezone': KST_TIMEZONE}
            if config.hour is not None: trigger_kwargs['hour'] = config.hour
            if config.minute is not None: trigger_kwargs['minute'] = config.minute
            if config.day is not None: trigger_kwargs['day'] = config.day
            if config.day_of_week is not None: trigger_kwargs['day_of_week'] = config.day_of_week

            scheduler.runner.add_job(
                func=config.func, trigger=config.trigger, **trigger_kwargs,
                id=config.job_id, name=config.name, misfire_grace_time=config.misfire_grace_time,
                max_instances=config.max_instances, replace_existing=True, coalesce=config.coalesce
            )
            self.schedules.append(config)
            logger.info(f"✅ 스케줄 등록 완료: {config.name} (ID: {config.job_id})")
        except Exception as e:
            logger.error(f"❌ 스케줄 등록 실패: {config.name} - {e}")

    def register_all(self) -> None:
        """모든 스케줄 등록 실행"""
        logger.info(f"스케줄링 작업 등록 시작 (환경: {self.current_env})")

        # --- 🚀 K-APT 신규 작업 등록 ---
        self.register(ScheduleConfig(
            func=job_building_raw_kapt_list,
            trigger='cron', hour=0, minute=0,
            job_id='building_raw_kapt_list',
            name='K-APT 단지 목록 수집',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_raw_kapt_basic,
            trigger='cron', hour=1, minute=0,
            job_id='building_raw_kapt_basic',
            name='K-APT 단지 기본정보 수집',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_raw_kapt_detail,
            trigger='cron', hour=2, minute=0,
            job_id='building_raw_kapt_detail',
            name='K-APT 단지 상세정보 수집',
            environments=['development', 'production']
        ))

        # --- 🚀 기존 작업 유지 (시간대 변경 없음) ---
        self.register(ScheduleConfig(
            func=job_location_raw_address_db,
            trigger='cron', hour=0, minute=0,
            job_id='location_raw_address_db_sync',
            name='도로명주소 원천 DB 다운로드 및 갱신',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_location_raw_road_code_sync,
            trigger='cron', hour=0, minute=30,
            job_id='job_location_raw_road_code_sync',
            name='도로 코드 마스터 데이터 임포트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_location_raw_road_address_sync,
            trigger='cron', hour=1, minute=0,
            job_id='location_raw_road_address_sync',
            name='도로명주소(건물) 마스터 데이터 임포트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_location_raw_block_address_sync,
            trigger='cron', hour=2, minute=0,
            job_id='location_raw_block_address_sync',
            name='관련지번 마스터 데이터 임포트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_location_raw_building_group_sync,
            trigger='cron', hour=3, minute=0,
            job_id='location_raw_building_group_sync',
            name='주소 부가정보 마스터 데이터 임포트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_boundary_update,
            trigger='cron', hour=0, minute=0,
            job_id='boundary_daily_update',
            name='지역경계 데이터 일일 업데이트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_raw_sync,
            trigger='cron', hour=1, minute=0,
            job_id='building_raw_sync_all',
            name='건축물대장 전체 정보 일괄 수집',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_structure_address_build,
            trigger='cron', hour=3, minute=0,
            job_id='building_structure_address_build',
            name='주소 기반 좌표 및 지적도 결합 빌드',
            environments=['development', 'production']
        ))


# --- 🛠️ 유틸리티 함수 및 외부 노출 ---

_registry = SchedulerRegistry()

def register_all_jobs() -> None:
    _registry.register_all()

def print_scheduled_jobs() -> None:
    try:
        jobs = scheduler.runner.get_jobs()
        if jobs:
            logger.info(f"현재 로드된 스케줄링 작업 ({len(jobs)}개):")
            for job in jobs:
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
                logger.info(f"  📅 {job.name} (ID: {job.id}) - 다음 실행: {next_run}")
    except Exception as e:
        logger.warning(f"작업 목록 조회 실패: {e}")

def get_scheduler():
    return scheduler

def get_job_status():
    print_scheduled_jobs()

def get_environment_schedules() -> Dict[str, List[str]]:
    env_schedules = {'local': [], 'development': [], 'production': []}
    for schedule in _registry.schedules:
        for env in schedule.environments:
            if env in env_schedules:
                env_schedules[env].append(schedule.name)
    return env_schedules

register_all_jobs()

__all__ = [
    'scheduler', 'register_all_jobs', 'print_scheduled_jobs',
    'get_scheduler', 'get_job_status', 'get_environment_schedules',
    'ScheduleConfig', 'SchedulerRegistry'
]