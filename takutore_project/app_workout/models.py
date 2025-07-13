from django.db import models
from django.contrib.auth import get_user_model  # ユーザーモデル対応
from app_video.models import Video  # Videoモデルの読み込み

User = get_user_model()

class WorkoutMenu(models.Model):
    workout_record = models.ForeignKey('WorkoutRecord', on_delete=models.CASCADE)  # 実際の運動記録と紐づけ（別テーブル）
    video = models.ForeignKey(Video, on_delete=models.CASCADE)  # 動画との紐づけ
    sequence = models.IntegerField()  # 表示順
    created_at = models.DateTimeField(auto_now_add=True)  # 自動登録
    updated_at = models.DateTimeField(auto_now=True)      # 自動更新

    class Meta:
        db_table = 'workout_menus'

class WorkoutRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 誰の記録か
    weight_record = models.FloatField(blank=True, null=True)  # 体重（任意）
    memo = models.TextField(blank=True, null=True)            # メモ（任意）
    created_at = models.DateTimeField()                       # 登録日時
    updated_at = models.DateTimeField(auto_now=True)          # 更新日時

    class Meta:
        db_table = 'workout_records'
    
    @property
    def save_workout_menu(self):
        # 紐づく WorkoutMenu を表示順に並べて video タイトルを列挙
        return " / ".join(
            wm.video.title for wm in self.workoutmenu_set.all().order_by("sequence")
        )

