from typing import List, Any

from app.services.message.webhook.managers.slack_manager import SlackManager
from app.services.message.webhook.services.abstract_service import AbstractService


class SlackService(AbstractService):
    def __init__(self, manager: SlackManager):
        self._manager = manager

    @property
    def manager(self) -> SlackManager:
        return self._manager

    @property
    def logger_name(self) -> str:
        return 'slack'

    def send_message(self, driver_name: str, items: List[Any]):
        self.manager.driver(driver_name).post(items)


