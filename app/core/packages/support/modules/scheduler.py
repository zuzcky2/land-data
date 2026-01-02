from apscheduler.schedulers.background import BlockingScheduler
from app.core.helpers.log import Log
from .command import Command
from logging import Logger


class Scheduler:
    """
    작업 스케줄링을 관리하는 클래스입니다.
    백그라운드 스케줄러를 사용하여 작업을 예약하고 로그를 관리합니다.

    Attributes:
        logger (Logger): 스케줄러 작업에 대한 로깅을 위한 Logger 인스턴스입니다.
        runner (BlockingScheduler): 작업을 실행하는 APScheduler의 BlockingScheduler 인스턴스입니다.
    """

    def __init__(self, command: Command):
        """
        Scheduler 클래스의 생성자로, 로깅 및 스케줄러 인스턴스를 초기화합니다.

        Args:
            log (Log): 로그 설정을 관리하는 Log 객체입니다.
        """
        self.logger = command.logger
        self.runner = self.create_instance()

    def create_instance(self) -> BlockingScheduler:
        """
        BlockingScheduler 인스턴스를 생성하여 반환합니다.

        Returns:
            BlockingScheduler: 작업을 스케줄링할 BlockingScheduler 인스턴스입니다.
        """
        return BlockingScheduler()

    def start(self):
        """
        스케줄러를 시작하여 예약된 작업을 실행합니다.
        """
        self.logger.info("스케줄러가 시작되었습니다.")
        self.runner.start()

    def stop(self):
        """
        스케줄러를 중지하여 모든 예약된 작업을 멈춥니다.
        """
        self.logger.info("스케줄러가 중지되었습니다.")
        self.runner.shutdown()


# 외부로 노출할 클래스 목록을 정의합니다.
__all__ = ['Scheduler']