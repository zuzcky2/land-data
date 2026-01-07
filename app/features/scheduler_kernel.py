"""스케줄러 커널 모듈

애플리케이션의 모든 백그라운드 작업을 등록하고 관리하는 중앙 집중식 스케줄러입니다.
"""

from typing import Optional, Callable, Dict, List, Union
import logging
from dataclasses import dataclass
from pytz import timezone

from app.facade import scheduler
from app.core.helpers.env import Env
from app.core.helpers.log import Log

# 스케줄러 전용 로거
logger: logging.Logger = Log.get_logger('scheduler')

# 기본 타임존 설정 (한국 시간)
KST_TIMEZONE = timezone('Asia/Seoul')


@dataclass
class ScheduleConfig:
    """스케줄 설정 데이터 클래스"""
    func: Callable
    trigger: str
    job_id: str
    name: str
    hour: Optional[int] = None
    minute: Optional[Union[int, str]] = None
    day: Optional[int] = None
    day_of_week: Optional[str] = None  # 요일별 스케줄 지원 추가
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
            logger.debug(
                f"스케줄 건너뜀: {config.name} "
                f"(현재: {self.current_env}, 허용: {config.environments})"
            )
            return

        try:
            # 크론 트리거 인자 구성
            trigger_kwargs = {
                'timezone': KST_TIMEZONE
            }

            if config.hour is not None:
                trigger_kwargs['hour'] = config.hour
            if config.minute is not None:
                trigger_kwargs['minute'] = config.minute
            if config.day is not None:
                trigger_kwargs['day'] = config.day
            if config.day_of_week is not None:
                trigger_kwargs['day_of_week'] = config.day_of_week

            # 작업 등록
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
            logger.info(f"✅ 스케줄 등록: {config.name} (ID: {config.job_id})")

        except Exception as e:
            logger.error(f"❌ 스케줄 등록 실패: {config.name} - {e}")

    def register_boundary_schedules(self) -> None:
        """지역 경계 데이터 스케줄 등록"""
        try:
            from app.features.location.boundary.command import BoundaryCommand
            boundary_cmd = BoundaryCommand()

            self.register(ScheduleConfig(
                func=boundary_cmd.write_boundary_all,
                trigger='cron',
                hour=0,
                minute=5,
                job_id='boundary_daily_update',
                name='지역경계 데이터 일일 업데이트',
                environments=['development', 'production']
            ))
        except ImportError as e:
            logger.error(f"지역경계 스케줄러 모듈 로드 실패: {e}")

    def register_building_raw_schedules(self) -> None:
        """건축물대장 원천 데이터 수집 스케줄 등록"""
        try:
            from app.features.building.raw.command import BuildingRawCommand
            building_cmd = BuildingRawCommand()

            self.register(ScheduleConfig(
                func=lambda: building_cmd.handle_sync_all(is_continue=True, is_renew=True),
                trigger='cron',
                hour=1,
                minute=0,
                job_id='building_raw_sync_all',
                name='건축물대장 전체 정보 일괄 수집',
                max_instances=1,
                coalesce=True,
                environments=['development', 'production']
            ))
        except ImportError as e:
            logger.error(f"건축물대장 스케줄러 모듈 로드 실패: {e}")

    def register_location_address_schedules(self) -> None:
        """건축물대장 기반 주소 및 공간정보 빌드 스케줄 등록"""
        try:
            from app.features.location.address.command import LocationAddressCommand
            address_cmd = LocationAddressCommand()

            # 1. 주소 동기화: 매월 1일 오후 09:00(21:00)
            self.register(ScheduleConfig(
                func=lambda: address_cmd.handle_sync_all(is_continue=True, is_renew=True),
                trigger='cron',
                day=1,
                hour=21,
                minute=0,
                job_id='location_address_sync_all',
                name='총괄, 표제부 기반 주소 동기화',
                max_instances=1,
                coalesce=True,
                environments=['development', 'production']
            ))

            # 2. 공간정보 빌드: 매주 월요일 오전 00:00
            self.register(ScheduleConfig(
                func=lambda: address_cmd.handle_build_address(is_continue=True, is_renew=True),
                trigger='cron',
                day_of_week='mon',
                hour=0,
                minute=0,
                job_id='location_address_build_spatial',
                name='주소 기반 좌표 및 지적도 결합 빌드',
                max_instances=1,
                coalesce=True,
                environments=['development', 'production']
            ))

        except ImportError as e:
            logger.error(f"주소/빌드 스케줄러 모듈 로드 실패: {e}")

    def register_test_schedules(self) -> None:
        """테스트 스케줄"""
        def test_logging_job():
            import datetime
            logger.info(f"🔔 [Scheduler Test] 현재 시간: {datetime.datetime.now(KST_TIMEZONE)}")

        self.register(ScheduleConfig(
            func=test_logging_job,
            trigger='cron',
            minute=30,
            job_id='scheduler_heartbeat_test',
            name='스케줄러 동작 테스트',
            environments=['local', 'development', 'production']
        ))

    def register_all(self) -> None:
        """모든 스케줄 등록"""
        logger.info(f"스케줄링 작업 등록 시작 (환경: {self.current_env})")
        self.register_boundary_schedules()
        self.register_building_raw_schedules()
        self.register_location_address_schedules()
        self.register_test_schedules()
        logger.info("스케줄링 작업 등록 완료")

    def print_jobs_after_start(self) -> None:
        self._print_registered_jobs()

    def _print_registered_jobs(self) -> None:
        try:
            jobs = scheduler.runner.get_jobs()
            if jobs:
                logger.info(f"등록된 스케줄링 작업 ({len(jobs)}개):")
                for job in jobs:
                    next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else 'N/A'
                    logger.info(f"  📅 {job.name} (ID: {job.id}) - 다음 실행: {next_run}")
            else:
                logger.warning("등록된 스케줄링 작업이 없습니다")
        except Exception as e:
            logger.warning(f"작업 목록 출력 중 오류 발생: {e}")


# 전역 인스턴스
_registry = SchedulerRegistry()

def register_all_jobs() -> None:
    _registry.register_all()

def print_scheduled_jobs() -> None:
    _registry.print_jobs_after_start()

def get_scheduler():
    return scheduler

def get_job_status() -> None:
    try:
        jobs = scheduler.runner.get_jobs()
        if not jobs:
            logger.info("현재 등록된 작업이 없습니다")
            return
        logger.info(f"현재 작업 상태 ({len(jobs)}개):")
        for job in jobs:
            logger.info(f"  🔧 작업: {job.name} (ID: {job.id}) - 트리거: {job.trigger}")
    except Exception as e:
        logger.error(f"❌ 작업 상태 조회 실패: {e}")

def get_environment_schedules() -> Dict[str, List[str]]:
    env_schedules = {'local': [], 'development': [], 'production': []}
    for schedule in _registry.schedules:
        for env in schedule.environments:
            if env in env_schedules:
                env_schedules[env].append(schedule.name)
    return env_schedules

# 모듈 로드 시 자동 등록
register_all_jobs()

# 외부 노출 필드 (변경 금지)
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