from app.services.message.webhook.managers.abstract_manager import AbstractManager
from app.services.message.webhook.drivers.slack.default_slack_driver \
    import (DefaultSlackDriver)
from app.services.message.webhook.drivers.slack.command_slack_driver \
    import (CommandSlackDriver)
from app.services.message.webhook.drivers.slack.scheduler_slack_driver \
    import (SchedulerSlackDriver)
from app.services.message.webhook.drivers.slack.queue_slack_driver \
    import (QueueSlackDriver)
from app.services.message.webhook.drivers.driver_interface \
    import (DriverInterface)


class SlackManager(AbstractManager):
    _default_driver: DefaultSlackDriver

    def __init__(self,
        default_driver: DefaultSlackDriver,
        command_driver: CommandSlackDriver,
        scheduler_driver: SchedulerSlackDriver,
        queue_driver: QueueSlackDriver,
    ):
        self._default_driver = default_driver
        self._command_driver = command_driver
        self._scheduler_driver = scheduler_driver
        self._queue_driver = queue_driver

    @property
    def default_driver(self) -> DriverInterface:
        return self._default_driver

    @property
    def command_driver(self) -> DriverInterface:
        return self._command_driver

    @property
    def scheduler_driver(self) -> DriverInterface:
        return self._scheduler_driver

    @property
    def queue_driver(self) -> DriverInterface:
        return self._queue_driver

    def _create_default_driver(self) -> DriverInterface:
        return self.default_driver

    def _create_command_driver(self) -> DriverInterface:
        return self.command_driver

    def _create_scheduler_driver(self) -> DriverInterface:
        return self.scheduler_driver

    def _create_queue_driver(self) -> DriverInterface:
        return self.queue_driver
