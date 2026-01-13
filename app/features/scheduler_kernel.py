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

def job_boundary_update():
    """지역 경계 데이터 업데이트 래퍼"""
    from app.features.location.boundary.command import BoundaryCommand
    execute_job(BoundaryCommand().write_boundary_all, "지역경계 데이터 일일 업데이트")

def job_building_raw_sync():
    """건축물대장 원천 데이터 동기화 래퍼"""
    from app.features.building.raw.command import BuildingRawCommand
    execute_job(BuildingRawCommand().handle_sync_all, "건축물대장 전체 정보 일괄 수집", is_continue=True, is_renew=True)

def job_location_address_sync():
    """주소 마스터 동기화 래퍼"""
    from app.features.location.raw.command import LocationRawCommand
    execute_job(LocationRawCommand().handle_sync_all, "총괄, 표제부 기반 주소 동기화", is_continue=False, is_renew=False)

def job_building_structure_build():
    """공간정보 빌드 래퍼"""
    from app.features.building.structure.command import StructureBuildCommand
    execute_job(StructureBuildCommand().handle, "주소 기반 좌표 및 지적도 결합 빌드", is_continue=False, is_renew=False)

@dataclass
class ScheduleConfig:
    """스케줄 설정 데이터 클래스"""
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
        """환경 설정 기본값"""
        if self.environments is None:
            self.environments = ['local', 'development', 'production']


class SchedulerRegistry:
    """스케줄러 작업 등록 관리 클래스"""

    def __init__(self):
        self.schedules: List[ScheduleConfig] = []
        self.current_env = Env.get('APP_ENV', 'local')

    def register(self, config: ScheduleConfig) -> None:
        """스케줄 등록"""
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
                func=config.func,
                trigger=config.trigger,
                **trigger_kwargs,
                id=config.job_id,
                name=config.name,
                misfire_grace_time=config.misfire_grace_time,
                max_instances=config.max_instances,
                replace_existing=True,
                coalesce=config.coalesce
            )

            self.schedules.append(config)
            logger.info(f"✅ 스케줄 등록 완료: {config.name} (ID: {config.job_id})")

        except Exception as e:
            logger.error(f"❌ 스케줄 등록 실패: {config.name} - {e}")

    def register_all(self) -> None:
        """모든 스케줄 등록 실행"""
        logger.info(f"스케줄링 작업 등록 시작 (환경: {self.current_env})")

        self.register(ScheduleConfig(
            func=job_boundary_update,
            trigger='cron',
            hour=0, minute=5,
            job_id='boundary_daily_update',
            name='지역경계 데이터 일일 업데이트',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_raw_sync,
            trigger='cron',
            hour=1, minute=0,
            job_id='building_raw_sync_all',
            name='건축물대장 전체 정보 일괄 수집',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_location_address_sync,
            trigger='cron',
            day=1, hour=21, minute=0,
            job_id='location_raw_address_sync_all',
            name='총괄, 표제부 기반 주소 동기화',
            environments=['development', 'production']
        ))

        self.register(ScheduleConfig(
            func=job_building_structure_build,
            trigger='cron',
            day_of_week='tue', hour=0, minute=0,
            job_id='building_structure_address_build',
            name='주소 기반 좌표 및 지적도 결합 빌드',
            environments=['development', 'production']
        ))


# --- 🛠️ 유틸리티 함수 및 외부 노출 ---

_registry = SchedulerRegistry()

def register_all_jobs() -> None:
    """애플리케이션 시작 시 호출"""
    _registry.register_all()

def print_scheduled_jobs() -> None:
    """현재 등록된 작업 목록 출력"""
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

# 모듈 로드 시 자동 등록
register_all_jobs()

__all__ = [
    'scheduler',
    'register_all_jobs',
    'print_scheduled_jobs',
    'get_scheduler',
    'get_job_status',
    'get_environment_schedules',
    'ScheduleConfig',
    'SchedulerRegistry'
]