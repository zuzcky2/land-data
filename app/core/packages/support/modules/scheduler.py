from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.jobstores.mongodb import MongoDBJobStore
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor

from app.core.helpers.log import Log
from app.core.packages.database.manager import Manager  # 매니저 타입 힌트용
from typing import Dict, Any


class Scheduler:
    """
    Database Manager를 통해 MongoDB JobStore를 사용하는 스케줄러입니다.
    """

    def __init__(self, database_manager: Manager):
        """
        Args:
            database_manager (Manager): 프레임워크의 DB 관리 인스턴스
        """
        self.logger = Log.get_logger('scheduler')

        # 1. 드라이버에서 클라이언트와 설정 정보 추출
        # get_mongodb_driver가 MongoClient를 반환한다고 가정합니다.
        self.mongo_client = database_manager.get_mongodb_driver('mongodb')
        self.db_name = "landmark"
        self.collection_name = "jobs"

        self.runner = self.create_instance()

    def create_instance(self) -> BlockingScheduler:
        """
        DB 매니저의 클라이언트를 주입하여 스케줄러 인스턴스를 생성합니다.
        """
        # 1. MongoDB JobStore 설정 (URI 대신 client 직접 전달)
        jobstores = {
            'default': MongoDBJobStore(
                client=self.mongo_client,
                database=self.db_name,
                collection=self.collection_name
            )
        }

        # 2. 실행기 설정 (4개 코어 프로세스 풀 포함)
        executors = {
            'default': ThreadPoolExecutor(20),
            'processpool': ProcessPoolExecutor(max_workers=4)
        }

        # 3. 기본 실행 정책 설정
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 3600
        }

        return BlockingScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='Asia/Seoul'
        )

    def start(self):
        """스케줄러 시작"""
        try:
            self.logger.info(f"MongoDB({self.db_name}.{self.collection_name}) 기반 스케줄러를 시작합니다.")
            self.runner.start()
        except (KeyboardInterrupt, SystemExit):
            self.stop()

    def stop(self):
        """스케줄러 중지"""
        if self.runner.running:
            self.logger.info("스케줄러를 안전하게 중지합니다.")
            self.runner.shutdown()

    def add_job(self, func, trigger, **kwargs):
        """
        작업 추가 메서드
        ID가 지정되지 않으면 함수의 이름을 기본 ID로 사용합니다.
        """
        job_id = kwargs.get('id', func.__name__)
        self.runner.add_job(
            func,
            trigger,
            replace_existing=True,
            **kwargs
        )
        self.logger.info(f"작업 예약 성공: {job_id}")


__all__ = ['Scheduler']