from django.db import models
from django.contrib.auth import get_user_model  # ユーザーモデル対応

User = get_user_model()

class Video(models.Model):
    TIME_CHOICES = {
        "0": "朝トレ",
        "1": "夜トレ",
    }

    TYPE_CHOICES = {
        "0": "ストレッチ",
        "1": "筋トレ",
        "2": "フォームローラー",
        "3": "マッサージ",
    }

    BODY_PART_CHOICES = {
        "0": "姿勢",
        "1": "全身",
        "2": "脚",
        "3": "お腹",
        "4": "上半身",
        "5": "骨盤矯正",
        "6": "顔",
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ユーザーと関連付け
    time_category = models.CharField(max_length=100, blank=True, null=True)  # 時間帯
    type_category = models.CharField(max_length=100, blank=True, null=True)  # 種別
    body_part_category = models.CharField(max_length=100, blank=True, null=True)  # 部位
    duration_time = models.CharField(max_length=5, blank=False)       # MM:SS 形式
    duration_seconds = models.IntegerField(default=0)             # 秒数
    youtuber_name = models.CharField(max_length=255)
    url = models.URLField()
    memo = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # 登録日時
    updated_at = models.DateTimeField(auto_now=True)  # 最終更新日時

    class Meta:
      db_table = 'videos'  # ここでテーブル名を指定

    def save(self, *args, **kwargs):
      if self.duration_time and ":" in self.duration_time:
        try:
            minutes, seconds = map(int, self.duration_time.split(":"))
            self.duration_seconds = minutes * 60 + seconds
        except ValueError:
            self.duration_seconds = 0  # 変換失敗時は 0秒 などの初期値に
      super().save(*args, **kwargs)

     # 追加: ラベル表示用
    def get_time_labels(self):
        return [self.TIME_CHOICES.get(val, val) for val in self.time_category.split(",") if val]

    def get_type_labels(self):
        return [self.TYPE_CHOICES.get(val, val) for val in self.type_category.split(",") if val]

    def get_body_part_labels(self):
        return [self.BODY_PART_CHOICES.get(val, val) for val in self.body_part_category.split(",") if val]
    
    # 埋め込み動画
    def get_embed_url(self):
      if self.url:
        if "watch?v=" in self.url:
            return self.url.replace("watch?v=", "embed/")
        elif "youtu.be/" in self.url:
            video_id = self.url.split("youtu.be/")[1]
            return f"https://www.youtube.com/embed/{video_id}"
        elif "shorts/" in self.url:
            video_id = self.url.split("shorts/")[1]
            return f"https://www.youtube.com/embed/{video_id}"
      return self.url