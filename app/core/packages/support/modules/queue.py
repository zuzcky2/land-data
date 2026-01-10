from typing import Type
from urllib.parse import quote_plus  # 🚀 필수 추가
from celery import Celery
from app.core.helpers.log import Log


class Queue:
    def __init__(self, broker_url: str, mongo_cfg: dict):
        self.logger = Log.get_logger('queue')

        # 🚀 팩트: 아이디와 비밀번호 내 특수문자를 RFC 3986 규격에 맞게 인코딩
        user = quote_plus(mongo_cfg.get('user', ''))
        password = quote_plus(mongo_cfg.get('password', ''))
        host = mongo_cfg.get('host', 'localhost')
        port = mongo_cfg.get('port', '27017')
        db_name = mongo_cfg.get('name', 'landmark')

        # 인코딩된 정보를 바탕으로 안전한 URI 생성
        result_url = f"mongodb://{user}:{password}@{host}:{port}/{db_name}?authSource={db_name}"

        self.app = Celery('landmark_queue', broker=broker_url, backend=result_url)
        self.app.conf.update(
            mongodb_backend_settings={
                'database': db_name,
                'taskmeta_collection': 'queue_results',
            },
            task_serializer='json',
            result_serializer='json',
            accept_content=['json'],
            timezone='Asia/Seoul',
            enable_utc=True,
            task_track_started=True,
            result_extended=True
        )

    def dispatch(self, job_class: Type, **payload):
        job_path = f"{job_class.__module__}.{job_class.__name__}"
        try:
            self.app.send_task(
                'app.queue.router',
                kwargs={'job_path': job_path, 'data': payload}
            )
            self.logger.info(f"📤 Dispatch Success: {job_path}")
        except Exception as e:
            self.logger.error(f"❌ Dispatch Failed: {str(e)}")