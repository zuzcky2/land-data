import sys
import importlib
import logging
from typing import Any

from app.core.runner import run_with_services
from app.core.logger import log_exception
from app.facade import queue
from app.core.helpers.log import Log

# 🚀 중요: facade.queue 내부에 선언된 celery 앱 인스턴스 참조
celery_app = queue.app

logger = Log.get_logger('queue')

@celery_app.task(name='app.queue.router', bind=True)
def queue_router(self, job_path: str, data: dict):
    """동적 Job 라우터"""
    try:
        logger.info(f"📥 Received Job: {job_path}")
        module_path, class_name = job_path.rsplit('.', 1)
        module = importlib.import_module(module_path)
        job_class = getattr(module, class_name)

        result = job_class().handle(**data)
        return {"job_class": job_path, "output": result}
    except Exception as e:
        logger.error(f"🔥 Job Failed: {job_path} - {str(e)}", exc_info=True)
        raise e


def run_worker(worker_logger: logging.Logger, log_config: Any) -> None:
    try:
        worker_logger.info("🟢 큐 워커 부트스트랩 완료 (Facade Queue 사용)")

        # 🚀 facade.queue.app을 통해 워커 실행
        # 모든 MongoDB 백엔드 설정이 여기에 포함되어 있습니다.
        celery_app.worker_main([
            'worker',
            '--loglevel=info',
            '--concurrency=1',
            '-n', 'landmark_worker@%h'
        ])
    except Exception as e:
        log_exception(worker_logger, "큐 워커 런타임", e)
        sys.exit(1)


def main() -> None:
    run_with_services(
        app_name='queue',
        main_fn=run_worker,
        bootstrap_condition=True
    )


if __name__ == '__main__':
    main()