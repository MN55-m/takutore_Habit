from django.apps import AppConfig


class AppVideoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_video'

    def ready(self):
        import app_video.signals  # signals.py を明示的に読み込む
