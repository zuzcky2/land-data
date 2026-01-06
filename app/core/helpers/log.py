import logging, traceback
import os, sys
from typing import Optional, Dict, Any
from datetime import datetime
import json
from fastapi import Request, HTTPException
from .env import Env
from .config import Config

class Log:
    """
    로깅 설정을 구성하고 로거 객체를 반환하는 클래스입니다.

    Attributes:
        default_logger_name (str): 기본 로거 이름. 로거 이름이 주어지지 않을 경우 사용됩니다.
        _initialized_loggers (dict)
    """
    default_logger_name = 'debug'
    _initialized_loggers = {}

    @staticmethod
    def get_logger(logger_name: Optional[str] = None) -> logging.Logger:
        logger_name = logger_name or Log.default_logger_name

        # 이미 초기화된 로거 반환
        if logger_name in Log._initialized_loggers:
            return Log._initialized_loggers[logger_name]

        logger_config: dict = Config.get(f'logging.{logger_name}')
        log_path = Env.get('LOG_PATH', '/var/volumes/log')
        log_filename = os.path.join(log_path, logger_config['filename'])

        # 🚀 [추가] 로그 파일이 저장될 디렉토리 생성
        log_dir = os.path.dirname(log_filename)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logger_config['level'])
        logger.propagate = False  # 중복 방지

        # ✅ 기존 핸들러가 있으면 모두 제거 (중복 방지)
        if logger.handlers:
            logger.handlers.clear()

        # ✅ FileHandler
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logger_config['level'])
        file_handler.setFormatter(logging.Formatter(logger_config['format']))
        logger.addHandler(file_handler)

        # ✅ StreamHandler (stdout → docker logs)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logger_config['level'])
        stream_handler.setFormatter(logging.Formatter(logger_config['format']))
        logger.addHandler(stream_handler)

        Log._initialized_loggers[logger_name] = logger
        return logger

    @staticmethod
    async def log_http_error(e: HTTPException, request: Request, logger_name: str = "api"):
        """
        HTTP 요청 중 발생한 오류를 JSON 형식으로 로깅합니다.

        Args:
            message (str): 오류 메시지입니다.
            request (Request): FastAPI Request 객체로부터 HTTP 요청 정보를 추출합니다.
            logger_name (str): 사용할 로거 이름입니다. 기본값은 "http"입니다.
        """
        logger = Log.get_logger(logger_name)
        context = await Log._build_context(request)

        print(logger_name)



        # 구조화된 스택 프레임
        tb_list = traceback.extract_tb(e.__traceback__)
        frames = []
        for frame in tb_list:
            frames.append({
                "file": frame.filename,
                "line": frame.lineno,
                "function": frame.name,
                "code": frame.line if frame.line else ""
            })

        log_data = {
            "message": e.detail,
            "context": context,
            "status_code": e.status_code,
            "level": "ERROR",
            "channel": logger_name,
            "datetime": {
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                "timezone_type": 3,
                "timezone": "Asia/Seoul"
            },
            "data": e.data if hasattr(e, 'data') else None,
            "traceback": frames,
            "extra": []
        }

        # JSON 형식으로 로그 기록
        logger.error(json.dumps(log_data, ensure_ascii=False, indent=4))

    @staticmethod
    async def _build_context(request: Request) -> Dict[str, Any]:
        """
        HTTP 요청의 상세 정보를 담은 context를 생성합니다.

        Args:
            request (Request): FastAPI Request 객체입니다.

        Returns:
            Dict[str, Any]: 요청 정보를 담은 context 딕셔너리입니다.
        """
        headers = {k: v for k, v in request.headers.items()}

        context = {
            "method": request.method,
            "header": {
                "userAgent": headers.get("user-agent"),
                "ip": headers.get("x-forwarded-for") or request.client.host,
                "referer": headers.get("referer")
            },
            "url": str(request.url),
            "pathParameter": request.path_params,
            "queryString": dict(request.query_params),
            "formData": await request.json() if request.method in ["POST", "PUT"] else {},
            "file": [],  # 파일 정보는 필요한 경우 추가 가능
            "reference": [],
            "provider": None
        }
        return context

    @staticmethod
    def get_config(logger_name: Optional[str] = None) -> dict:
        """
        uvicorn.run()에 넘길 수 있는 dict 형태의 logging config를 반환합니다.
        """
        logger_name = logger_name or Log.default_logger_name
        logger_config: dict = Config.get(f'logging.{logger_name}')
        log_path = Env.get('LOG_PATH', '/var/volumes/log')
        log_filename = os.path.join(log_path, logger_config['filename'])

        loggers = {
            logger_name: {
                "handlers": ["file", "console"],
                "level": logger_config["level"],
                "propagate": False,
            }
        }

        # ✅ uvicorn 전용 내부 로거들도 같이 설정
        if logger_name == "uvicorn":
            loggers.update({
                "uvicorn": {
                    "handlers": ["file", "console"],
                    "level": logger_config["level"],
                    "propagate": False,
                }
            })

        return {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": logger_config["format"],
                },
            },
            "handlers": {
                "file": {
                    "class": "logging.FileHandler",
                    "filename": log_filename,
                    "formatter": "default",
                    "level": logger_config["level"],
                },
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                    "level": logger_config["level"],
                },
            },
            "loggers": loggers,
        }


# 외부로 노출할 클래스 목록을 정의합니다.
__all__ = ['Log', 'logging']