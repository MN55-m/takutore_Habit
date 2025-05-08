from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    """
    動画登録用のフォームクラス
    """

    # 選択肢（文字列で扱う）
    TIME_CHOICES = [
        ("0", "朝トレ"),
        ("1", "夜トレ"),
    ]

    TYPE_CHOICES = [
        ("0", "ストレッチ"),
        ("1", "筋トレ"),
        ("2", "フォームローラー"),
        ("3", "マッサージ"),
    ]

    BODY_CHOICES = [
        ("0", "姿勢"),
        ("1", "全身"),
        ("2", "脚"),
        ("3", "お腹"),
        ("4", "上半身"),
        ("5", "骨盤矯正"),
        ("6", "顔"),
    ]

    # 複数選択できるフィールド（プルダウン形式）
    time_category = forms.MultipleChoiceField(
        choices=TIME_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        label="◆時間帯", required=True,
    )
    type_category = forms.MultipleChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        label="◆トレーニング種別", required=True,
    )
    body_part_category = forms.MultipleChoiceField(
        choices=BODY_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        label="◆部位", required=True,
    )

    class Meta:
        model = Video
        fields = [
            'time_category',
            'type_category',
            'body_part_category',
            'duration_time',  # ← ここが実際にフォームで使うフィールド
            'youtuber_name',
            'url',
            'memo'
        ]

        widgets = {
            'duration_time': forms.TextInput(attrs={'placeholder': 'MM:SS 形式で入力'}),  # ← 追加
            'youtuber_name': forms.TextInput(attrs={'placeholder': '例: ひなちゃん'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://~'}),
            'memo': forms.Textarea(attrs={'placeholder': '動画のタイトルやメモ'}),
        }
    
    # ここでカンマ区切りに変換
    def clean_time_category(self):
        data = self.cleaned_data['time_category']
        return ",".join(data)

    def clean_type_category(self):
        data = self.cleaned_data['type_category']
        return ",".join(data)

    def clean_body_part_category(self):
        data = self.cleaned_data['body_part_category']
        return ",".join(data)
    
    def clean_duration_time(self):
        """
        MM:SS 形式で入力された時間を検証し、正しい形式であることを確認
        """
        duration = self.cleaned_data.get('duration_time')

        if not duration:
            raise forms.ValidationError("動画時間を入力してください。")

        try:
            minutes, seconds = map(int, duration.split(":"))
            if minutes < 0 or seconds < 0 or seconds >= 60:
                raise ValueError
        except ValueError:
            raise forms.ValidationError("時間の形式は MM:SS で入力してください。")

        return duration

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # instanceが渡されている場合（編集画面の時）
        if self.instance and self.instance.pk:
            # モデルのカンマ区切り → リストに分割
            self.initial['time_category'] = self.instance.time_category.split(",") if self.instance.time_category else []
            self.initial['type_category'] = self.instance.type_category.split(",") if self.instance.type_category else []
            self.initial['body_part_category'] = self.instance.body_part_category.split(",") if self.instance.body_part_category else []