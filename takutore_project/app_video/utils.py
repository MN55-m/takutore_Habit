# app_video/utils.py
from app_video.models import Video

def ensure_user_has_default_videos(user):
    default_videos = Video.objects.filter(is_template=True, user=None)
    for dv in default_videos:
        # ✅ すでに同じURLのコピーがある場合はスキップ
        if not Video.objects.filter(user=user, url=dv.url).exists():
            Video.objects.create(
                user=user,
                is_template=False,
                time_category=dv.time_category,
                type_category=dv.type_category,
                body_part_category=dv.body_part_category,
                duration_time=dv.duration_time,
                duration_seconds=dv.duration_seconds,
                youtuber_name=dv.youtuber_name,
                url=dv.url,
                memo=dv.memo
            )
