from django import forms  # Djangoのフォーム機能をインポート
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User # 作成したモデルをインポート
from django.contrib.auth import authenticate

#新規アカウント登録
class SignupForm(UserCreationForm):
    class Meta:
        model = User  # 対応するモデルを指定
        fields = ["username", "email", "password1", "password2", "height", "weight"] # フォームに表示するフィールドを指定

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("このメールアドレスは、既に登録されています")
        return email

#ログイン
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField()

    def clean(self):
        print("ログインホームのcleanが呼び出された")
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        print(email, password)
        self.user = authenticate(email=email, password=password)
        if self.user is None:
            raise forms.ValidationError("認証に失敗しました")
        return self.cleaned_data

#マイページ
class MypageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'height', 'weight']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

#パスワード
class PasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        label="現在のパスワード", 
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'readonly': 'readonly'})
    )
    new_password1 = forms.CharField(
        label="新しいパスワード", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）", 
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']