"""스케줄러 커널 모듈

애플리케이션의 모든 백그라운드 작업을 등록하고 관리하는 중앙 집중식 스케줄러입니다.

주요 기능:
    - 환경별(local/개발/운영) 다른 스케줄링 정책 적용
    - 서비스별 스케줄링 작업 등록 및 관리
    - 타임존 관리 (한국 시간 기준)
    - 크론 스케줄링 및 작업 상태 모니터링

지원 서비스:
    - 지역 경계 데이터 (VWorld API 동기화)
    - 매물 범위 카테고리 (가격/면적 분류)
    - 매물 동기화 (MySQL ↔ OpenSearch)
    - 마케팅 사용자 세그먼트
    - 기본 인프라 동기화 (단지, 동, 층, 호, 지하철)
    - 통합검색 동기화 (Boundary, Metro, Building, House)
"""

from typing import Optional, Callable, Dict, List, Union
import logging
from dataclasses import dataclass
from pytz import timezone

from app.facade import scheduler
from app.core.helpers.env import Env

# 스케줄러 전용 로거
logger: logging.Logger = logging.getLogger('scheduler')

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
    misfire_grace_time: int = 300
    max_instances: int = 1
    coalesce: bool = False
    environments: List[str] = None  # ['local', 'development', 'production']

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
        """
        스케줄 등록

        Args:
            config: 스케줄 설정
        """
        # 현재 환경이 허용된 환경인지 확인
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

            # 매일 새벽 00:05 - 지역 경계 데이터 업데이트
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

            # 커맨드 인스턴스 생성
            building_cmd = BuildingRawCommand()

            # 매일 오전 00:00 실행
            # max_instances=1: 이전 작업이 끝나지 않았으면 새 작업을 시작하지 않음
            # coalesce=True: 시스템 장애 등으로 밀린 작업이 있어도 한 번만 실행
            self.register(ScheduleConfig(
                func=lambda: building_cmd.sync_all(is_continue=True, is_renew=True),
                trigger='cron',
                hour=0,
                minute=0,
                job_id='building_raw_sync_all',
                name='건축물대장 전체 정보 일괄 수집 (병렬)',
                max_instances=1,
                coalesce=True,
                environments=['development', 'production']
            ))

        except ImportError as e:
            logger.error(f"건축물대장 스케줄러 모듈 로드 실패: {e}")


    def register_all(self) -> None:
        """모든 스케줄 등록"""
        logger.info(f"스케줄링 작업 등록 시작 (환경: {self.current_env})")

        # 각 서비스별 스케줄 등록
        self.register_boundary_schedules()
        self.register_building_raw_schedules()

        logger.info("스케줄링 작업 등록 완료")

    def print_jobs_after_start(self) -> None:
        """스케줄러 시작 후 작업 목록 출력"""
        self._print_registered_jobs()

    def _print_registered_jobs(self) -> None:
        """등록된 작업 목록 출력"""
        try:
            jobs = scheduler.runner.get_jobs()
            if jobs:
                logger.info(f"등록된 스케줄링 작업 ({len(jobs)}개):")
                for job in jobs:
                    job_id = getattr(job, 'id', 'Unknown')
                    job_name = getattr(job, 'name', 'Unknown')

                    try:
                        if hasattr(job, 'next_run_time') and job.next_run_time:
                            next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            next_run = 'N/A'
                    except (AttributeError, TypeError):
                        next_run = 'N/A'

                    logger.info(f"  📅 {job_name} (ID: {job_id}) - 다음 실행: {next_run}")
            else:
                logger.warning("등록된 스케줄링 작업이 없습니다")

        except Exception as e:
            logger.warning(f"작업 목록 출력 중 오류 발생: {e}")


# =================================================================
# 전역 레지스트리 인스턴스 및 편의 함수
# =================================================================

_registry = SchedulerRegistry()


def register_all_jobs() -> None:
    """
    모든 스케줄링 작업 등록 (진입점)

    환경별로 적절한 스케줄링 작업들을 등록합니다.
    """
    _registry.register_all()


def print_scheduled_jobs() -> None:
    """
    스케줄러 시작 후 등록된 작업 목록 출력

    스케줄러가 시작된 후에 호출해야 next_run_time이 정상적으로 표시됩니다.
    """
    _registry.print_jobs_after_start()


def get_scheduler():
    """
    설정된 스케줄러 인스턴스 반환

    Returns:
        scheduler: APScheduler 인스턴스
    """
    return scheduler


def get_job_status() -> None:
    """
    현재 등록된 작업들의 상태 출력

    등록된 모든 스케줄링 작업의 상태와 정보를 로그로 출력합니다.
    """
    try:
        jobs = scheduler.runner.get_jobs()
        if not jobs:
            logger.info("현재 등록된 작업이 없습니다")
            return

        logger.info(f"현재 작업 상태 ({len(jobs)}개):")
        for job in jobs:
            try:
                job_id = getattr(job, 'id', 'Unknown')
                job_name = getattr(job, 'name', 'Unknown')
                logger.info(f"  🔧 작업: {job_name} (ID: {job_id})")

                if hasattr(job, 'trigger'):
                    logger.info(f"    ⏰ 트리거: {job.trigger}")

            except Exception as job_error:
                logger.warning(f"    ⚠️  작업 정보 조회 실패: {job_error}")

    except Exception as e:
        logger.error(f"❌ 작업 상태 조회 실패: {e}")


def get_environment_schedules() -> Dict[str, List[str]]:
    """
    환경별 등록된 스케줄 정보 반환

    Returns:
        환경별 스케줄 딕셔너리
    """
    env_schedules = {
        'local': [],
        'development': [],
        'production': []
    }

    for schedule in _registry.schedules:
        for env in schedule.environments:
            if env in env_schedules:
                env_schedules[env].append(schedule.name)

    return env_schedules


# 모듈 로드 시점에 모든 작업 자동 등록
register_all_jobs()

# 외부로 노출할 함수 및 객체 지정
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