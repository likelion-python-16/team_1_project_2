# diaries/apps.py
from django.apps import AppConfig

class DiariesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'diaries'

    def ready(self):
        import diaries.models  # 시그널이 models.py 안에 있으니 그대로 import
