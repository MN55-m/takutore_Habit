from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app_video.models import Video

User = get_user_model()

class Command(BaseCommand):
    help = "全てのデフォルト動画を各ユーザーに強制コピーします（既存コピーがあっても追加）"

    def handle(self, *args, **options):
        default_videos = Video.objects.filter(is_template=True, user=None)
        users = User.objects.all()
        count_created = 0

        for user in users:
            for dv in default_videos:
                # ✅ 存在チェックなし → 何度でもコピーされる
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
                    memo=dv.memo,
                )
                count_created += 1
            self.stdout.write(self.style.SUCCESS(f"{user.username} に {default_videos.count()} 件コピーしました"))

        self.stdout.write(self.style.SUCCESS(f"✅ 完了: {count_created} 件の動画をコピーしました"))
