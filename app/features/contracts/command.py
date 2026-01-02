from app.facade import command
from abc import ABC, abstractmethod

class AbstractCommand:

    def _handle_error(self, e, context=""):
        """에러 처리 공통 로직"""
        command.message(f'실행에 실패하였습니다. {context}', fg='red')
        command.error_log(str(e))
        raise e

    @abstractmethod
    def register_commands(self, cli_group):
        pass