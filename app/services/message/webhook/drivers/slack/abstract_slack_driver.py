from abc import ABC, abstractmethod
import requests
from typing import List, Any
from app.services.message.webhook.drivers.driver_interface import DriverInterface
from app.core.helpers.config import Config
from app.core.helpers.log import Log


class AbstractSlackDriver(ABC):
    """
    슬랙 웹훅 전송 추상 드라이버.
    상속받는 클래스에서 반드시 channel 프로퍼티를 구현해야 합니다.
    """

    def __init__(self):
        self.logger = Log.get_logger('slack')

        # 🚀 팩트: 하위 클래스에서 정의한 channel 프로퍼티 값을 기반으로 URL 로드
        channel_name = self.channel

        if channel_name == 'default':
            self.webhook_url = Config.get('message.webhook.slack.host')
        else:
            self.webhook_url = Config.get(f'message.webhook.slack.channels.{channel_name}')

    @property
    @abstractmethod
    def channel(self) -> str:
        """슬랙 채널 키를 정의합니다 (config/message.py 내 정의된 키)"""
        pass

    def post(self, items: List[Any]) -> Any:
        """데이터를 슬랙으로 전송합니다."""
        if not self.webhook_url:
            self.logger.error(f"❌ Slack Webhook URL 미설정 채널: {self.channel}")
            return False

        results = []
        for item in items:
            try:
                # 🚀 데이터 정규화 로직 개선
                if isinstance(item, str):
                    payload = {"text": item}
                elif isinstance(item, dict):
                    # 1. 이미 'text'나 'blocks'가 있다면 그대로 사용
                    if 'text' in item or 'blocks' in item:
                        payload = item
                    # 2. 'text' 키가 없으면 딕셔너리 전체를 문자열로 변환하여 'text'에 담음
                    else:
                        payload = {"text": str(item)}
                else:
                    payload = {"text": str(item)}

                response = requests.post(self.webhook_url, json=payload, timeout=5)

                if response.status_code == 200:
                    results.append(True)
                else:
                    # 상세 에러 파악을 위해 payload도 같이 찍어주면 좋습니다.
                    self.logger.error(f"❌ 슬랙 전송 실패 [{response.status_code}]: {response.text} | Payload: {payload}")
                    results.append(False)

            except Exception as e:
                self.logger.error(f"🔥 슬랙 드라이버 런타임 에러: {str(e)}")
                results.append(False)

        return results


__all__ = ['AbstractSlackDriver']