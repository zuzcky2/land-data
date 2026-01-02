import click
import time
from logging import Logger
from typing import Optional
from app.core.helpers.kst import Kst
from app.core.helpers.log import Log


class Command:
    """
    CLI 명령어를 관리하는 클래스입니다.

    Attributes:
        logger (Logger): 커맨드 로깅을 위한 Logger 인스턴스.
        start_time (float): 명령어 실행 시작 시간을 저장합니다.
    """

    def __init__(self):
        """
        Command 클래스 생성자로 필요한 객체들을 초기화합니다.
        """
        self.logger = Log.get_logger('command')
        self.start_time = time.perf_counter()  # 시작 시간을 기록합니다.

    def message(self, msg: str, fg: str = 'white', bg: str = 'black', logging: Optional[str] = None):
        """
        실행 시간과 메시지를 스타일링하여 출력하고 로그에 기록합니다.

        Args:
            msg (str): 출력할 메시지입니다.
            fg (str): 텍스트 색상. 기본값은 'white'입니다.
            bg (str): 배경 색상. 기본값은 'black'입니다.
            logging (Optional[str]): 로깅 레벨 ('error', 'warning', 'info') 중 하나입니다.
        """
        # 현재 시간과 실행 경과 시간을 스타일링하여 출력 메시지를 생성합니다.
        current_time = Kst.now().strftime("%Y-%m-%d %H:%M:%S")
        elapsed_time = time.perf_counter() - self.start_time

        # 출력할 메시지를 스타일링합니다.
        run_time = click.style(f"[RUN:{current_time}]", fg='magenta', bg='black')
        work_time = click.style(f"[WORK:{elapsed_time:.4f}]", fg='bright_blue', bg='black')
        text = click.style(f" {msg}", fg=fg, bg=bg)

        # 최종 메시지를 콘솔에 출력합니다.
        click.echo(run_time + work_time + text)

        # 로그 레벨에 따라 메시지를 기록합니다.
        if logging:
            self._log_message(print_msg=msg, level=logging)

        # 메시지 출력 후 시작 시간을 갱신하여 다음 작업 시간을 기록합니다.
        self.start_time = time.perf_counter()

    def _log_message(self, print_msg: str, level: str):
        """
        지정된 로깅 레벨에 따라 로그 메시지를 기록합니다.

        Args:
            print_msg (str): 로그에 기록할 메시지.
            level (str): 로깅 레벨 ('error', 'warning', 'info') 중 하나입니다.
        """
        if level == 'error':
            self.error_log(print_msg)
        elif level == 'warning':
            self.logger.warning(print_msg)
        else:
            self.logger.info(print_msg)

    def confirm(self) -> bool:
        """
        작업을 진행할지 사용자 확인을 요청합니다.

        Returns:
            bool: 사용자가 작업을 확인하면 True, 아니면 False를 반환합니다.
        """
        # 작업 진행 여부를 사용자에게 확인합니다.
        if not click.confirm('해당 작업을 진행하면 되돌릴 수 없습니다. 진행하시겠습니까?'):
            self.message('작업이 취소되었습니다.', fg='red')
            return False
        return True

    @click.group()
    @staticmethod
    def cli(**kwargs):
        """
        CLI 명령어 그룹을 정의합니다. 이 메서드는 click.group 데코레이터를 사용합니다.
        """
        pass

    def error_log(self, msg: str):
        """
        오류 메시지를 로깅하고, 전체 예외 스택 추적을 출력합니다.

        Args:
            msg (str): 로그에 기록할 오류 메시지입니다.
        """
        self.logger.error(msg, exc_info=True)


# 외부에 노출할 클래스 목록을 정의합니다.
__all__ = ['Command']