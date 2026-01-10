from dataclasses import dataclass
from dependency_injector.wiring import Provide, inject
from app.core.service.service_cache import get_service_with_cache
from app.services.message.webhook.container import WebhookContainer
from app.services.message.webhook.services.slack_service import SlackService


@dataclass
class WebhookFacade:
    slack_service: SlackService

@inject
def get_service(
    _slack_service: SlackService = Provide[WebhookContainer.slack_service],
) -> WebhookFacade:
    return WebhookFacade(
        slack_service=_slack_service,
    )

# 의존성 주입을 위한 Container 인스턴스 생성
application = WebhookContainer()

# 컨테이너의 구성 요소를 현재 모듈에 와이어링
application.wire(modules=[__name__])

facade: WebhookFacade = get_service_with_cache('message_webhook', get_service)


# 외부로 노출할 변수들을 지정합니다.
__all__ = ['facade']