from django import forms
from .models import Video

class VideoForm(forms.ModelForm):
    """
    動画登録用のフォームクラス
    """

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
            'time_category': forms.Select(choices=Video.TIME_CHOICES),
            'type_category': forms.Select(choices=Video.TYPE_CHOICES),
            'body_part_category': forms.Select(choices=Video.BODY_PART_CHOICES),
            'duration_time': forms.TextInput(attrs={'placeholder': 'MM:SS 形式で入力'}),  # ← 追加
            'youtuber_name': forms.TextInput(attrs={'placeholder': '例: ひなちゃん'}),
            'url': forms.URLInput(attrs={'placeholder': 'https://~'}),
            'memo': forms.Textarea(attrs={'placeholder': '動画のタイトルやメモ'}),
        }

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
