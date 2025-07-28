# app_video/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from app_video.models import Video  #  正しいモデル参照

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_videos(sender, instance, created, **kwargs):
    if created:
        #  user=None の共有テンプレートのみコピー
        template_videos = Video.objects.filter(is_template=True, user=None)
        for video in template_videos:
            Video.objects.create(
                user=instance,
                is_template=False,  # コピー側は削除可能
                time_category=video.time_category,
                type_category=video.type_category,
                body_part_category=video.body_part_category,
                duration_time=video.duration_time,
                duration_seconds=video.duration_seconds,  #  秒数もコピー
                youtuber_name=video.youtuber_name,
                url=video.url,
                memo=video.memo
            )
