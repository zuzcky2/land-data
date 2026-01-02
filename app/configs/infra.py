from app.core.helpers.env import Env


configs: dict = {
    'bucket_name': Env.get('BUILDING_BUCKET_NAME', ''),
    'file_path': Env.get('BUILDING_FILE_PATH', ''),
}

__all__ = ['configs']