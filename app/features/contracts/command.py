from abc import ABC, abstractmethod
from app.facade import command
from app.services.message.webhook import facade as webhook_facade

class AbstractCommand(ABC):

    def message(self, *args, **kwargs):
        """기존 command.message 브릿지"""
        return command.message(*args, **kwargs)

    def error_log(self, *args, **kwargs):
        """기존 command.error_log 브릿지"""
        return command.error_log(*args, **kwargs)

    def _send_slack(self, msg: str, status: str = "INFO"):
        """슬랙 메시지 발송 공통 로직"""
        try:
            emoji = "✅" if status == "INFO" else "🔥" if status == "ERROR" else "📢"
            class_name = self.__class__.__name__
            formatted_msg = f"{emoji} *[{class_name}]* {msg}"
            webhook_facade.slack_service.send_message('command', [formatted_msg])
        except Exception as e:
            command.error_log(f"Slack Send Failed: {str(e)}")

    def _handle_error(self, e, context=""):
        """에러 발생 시 공통 처리"""
        error_msg = f'실행에 실패하였습니다. {context}'
        self.message(error_msg, fg='red')
        # 에러 발생 슬랙 알림
        self._send_slack(f"{error_msg}\n> {str(e)}", status="ERROR")
        self.error_log(str(e))
        raise e

    @abstractmethod
    def register_commands(self, cli_group):
        pass