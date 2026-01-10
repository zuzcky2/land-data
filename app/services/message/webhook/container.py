from app.core.packages.support.abstracts.abstract_container import AbstractContainer, providers
from app.services.message.webhook.drivers.slack.command_slack_driver import CommandSlackDriver
from app.services.message.webhook.drivers.slack.default_slack_driver import DefaultSlackDriver
from app.services.message.webhook.drivers.slack.queue_slack_driver import QueueSlackDriver
from app.services.message.webhook.drivers.slack.scheduler_slack_driver import SchedulerSlackDriver
from app.services.message.webhook.managers.slack_manager import SlackManager
from app.services.message.webhook.services.slack_service import SlackService


class WebhookContainer(AbstractContainer):

    default_slack_driver: DefaultSlackDriver = providers.Factory(DefaultSlackDriver)
    command_slack_driver: CommandSlackDriver = providers.Factory(CommandSlackDriver)
    scheduler_slack_driver: SchedulerSlackDriver = providers.Factory(SchedulerSlackDriver)
    queue_slack_driver: QueueSlackDriver = providers.Factory(QueueSlackDriver)

    slack_manager: SlackManager = providers.Singleton(
        SlackManager,
        default_driver=default_slack_driver,
        command_driver=command_slack_driver,
        scheduler_driver=scheduler_slack_driver,
        queue_driver=queue_slack_driver,
    )
    slack_service: SlackService = providers.Singleton(
        SlackService,
        manager=slack_manager,
    )