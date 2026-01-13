import ast
import os
import re
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from app.facade import command
from app.services.message.webhook import facade as webhook_facade
from app.core.helpers.config import Config
from app.core.helpers.env import Env

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

    def _get_last_sync_point(self, service, source_type: Optional[str] = None, renew_days: int = 7) -> Optional[dict]:
        """
        로그 파일(.log 및 .log.1)을 분석하여 마지막 성공 지점을 반환합니다.
        공통화를 위해 source_type 유무에 따른 logger_name 처리를 포함합니다.
        """
        try:
            # 서비스에 따른 로거 이름 결정
            logger_name = service.logger_name
            if source_type:
                logger_name = f"{logger_name}_{source_type}"

            # 로깅 설정 가져오기
            logger_config = Config.get(f'logging.{logger_name}')
            if not logger_config and source_type:
                # 상세 설정이 없으면 기본 서비스 로거 설정 사용
                logger_config = Config.get(f'logging.{service.logger_name}')

            if not logger_config:
                return None

            log_path = Env.get('LOG_PATH', '/var/volumes/log')
            base_filename = os.path.join(log_path, logger_config['filename'])

            # 로테이션 대응 파일 리스트
            files_to_check = [base_filename, f"{base_filename}.1"]

            for log_filename in files_to_check:
                if not os.path.exists(log_filename) or os.path.getsize(log_filename) == 0:
                    continue

                with open(log_filename, 'r', encoding='utf-8') as f:
                    try:
                        lines = f.readlines()[-100:]
                    except EOFError:
                        continue

                    if not lines:
                        continue

                    for line in reversed(lines):
                        if "Sync Start: " in line:
                            # 1. 타임스탬프 분석
                            date_match = re.search(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
                            if date_match:
                                log_time = datetime.strptime(date_match.group(1), "%Y-%m-%d %H:%M:%S")
                                if datetime.now() - log_time > timedelta(days=renew_days):
                                    self.message(f"⚠️ [{logger_name}] 로그 기록이 {renew_days}일을 초과하여 처음부터 시작합니다.",
                                                 fg='yellow')
                                    return None

                            # 2. 파라미터(dict) 추출
                            param_match = re.search(r"Sync Start: (\{.*\})", line)
                            if param_match:
                                self.message(f"🔍 로그 지점 확인됨: {os.path.basename(log_filename)}", fg='white')

                                param_str = param_match.group(1)

                                # 1. ObjectId('...') -> '...' 치환
                                param_str = re.sub(r"ObjectId\(['\"]?([a-f0-9]{24})['\"]?\)", r"'\1'", param_str)

                                # 2. datetime.datetime(...) -> 문자열로 치환 (정규표현식)
                                # datetime.datetime(2025, 10, 14, ...) 형태를 찾아 따옴표로 감싸 문자열로 만듭니다.
                                param_str = re.sub(r"datetime\.datetime\([\d\s,]+\)", r"'datetime_object'", param_str)

                                try:
                                    # 이제 순수 리터럴들만 남았으므로 파싱 가능
                                    return ast.literal_eval(param_str)
                                except (ValueError, SyntaxError) as e:
                                    self.message(f"⚠️ 로그 파싱 실패: {e}", fg='yellow')
                                    return None

        except Exception as e:
            self.message(f"⚠️ 로그 분석 중 오류 발생: {e}", fg='yellow')

        return None

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