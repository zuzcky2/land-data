# app/configs/message.py

from app.core.helpers.env import Env

configs: dict = {
    'webhook': {
        'default_driver': 'slack',
        'slack': {
            # 기본 채널 (하위 호환성)
            'default': Env.get('SLACK_WEBHOOK_HOST', ''),
            # 채널별 확장 (필요 시 추가)
            'channels': {
                'command': Env.get('SLACK_WEBHOOK_INFO', Env.get('SLACK_WEBHOOK_COMMAND_HOST', '')),
                'scheduler': Env.get('SLACK_WEBHOOK_ERROR', Env.get('SLACK_WEBHOOK_SCHEDULER_HOST', '')),
                'queue': Env.get('SLACK_WEBHOOK_LOG', Env.get('SLACK_WEBHOOK_QUEUE_HOST', '')),
            }
        }
    }
}