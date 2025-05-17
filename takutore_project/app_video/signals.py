# app_workout/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Video

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_videos(sender, instance, created, **kwargs):
    if created:
        # テンプレ動画を全て取得
        template_videos = Video.objects.filter(is_template=True)
        for video in template_videos:
            Video.objects.create(
                user=instance,
                is_template=False,  # 複製側はテンプレ扱いではない
                time_category=video.time_category,
                type_category=video.type_category,
                body_part_category=video.body_part_category,
                duration_time=video.duration_time,
                youtuber_name=video.youtuber_name,
                url=video.url,
                memo=video.memo
            )
