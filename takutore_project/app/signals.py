from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from app_video.utils import ensure_user_has_default_videos

User = get_user_model()

@receiver(post_save, sender=User)
def create_default_videos_for_new_user(sender, instance, created, **kwargs):
    if created:  # ✅ 新規作成ユーザーのみ
        ensure_user_has_default_videos(instance)
