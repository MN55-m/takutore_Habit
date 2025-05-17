from django import forms
from .models import WorkoutMenu


class WorkoutSettingForm(forms.Form):
    PART_CHOICES = [
        ("0", "姿勢"),
        ("1", "全身"),
        ("2", "脚"),
        ("3", "お腹"),
        ("4", "上半身"),
        ("5", "骨盤矯正"),
        ("6", "顔"),
    ]

    TYPE_CHOICES = [
        ("0", "ストレッチ"),
        ("1", "筋トレ"),
        ("2", "フォームローラー"),
        ("3", "マッサージ"),
    ]

    duration = forms.IntegerField(
        widget=forms.NumberInput(attrs={'step': 1, 'min': 1, 'placeholder': 'mm'}),
        label='◆トレーニング時間（分）', required=True)
    parts = forms.MultipleChoiceField(
        choices=PART_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}), 
        label='◆トレーニング部位 (複数選択可)', required=True)
    types = forms.MultipleChoiceField(
        choices=TYPE_CHOICES,
        widget=forms.SelectMultiple(attrs={'class': 'select2'}), 
        label='◆トレーニング種別 (複数選択可)', required=True)

# WorkoutMenu を登録するためのフォームを定義
class WorkoutMenuForm(forms.ModelForm):
    class Meta:
        model = WorkoutMenu  # 使用するモデル
        fields = ['video', 'sequence']  # 入力対象フィールド（video と 表示順）