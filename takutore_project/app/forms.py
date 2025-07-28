from django import forms  # Djangoのフォーム機能をインポート
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()  # カスタムユーザーモデルを取得

#新規アカウント登録
class SignupForm(UserCreationForm):
    password1 = forms.CharField(label="password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="password(確認)", widget=forms.PasswordInput)

    height = forms.FloatField(required=True, label="身長")
    weight = forms.FloatField(required=True, label="体重")

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
    # パスワードを入力するためのフィールド
    # PasswordInputはパスワードを非表示にして表示する
    old_password = forms.CharField(
        label="現在のパスワード", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password'}))
    new_password1 = forms.CharField(
        label="新しいパスワード", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))
    new_password2 = forms.CharField(
        label="新しいパスワード（確認）", 
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}))

    # フォームで使用するモデルとフィールドを設定
    class Meta:
        model = User # Userモデルを使って、ユーザー情報を管理
        fields = ['old_password', 'new_password1', 'new_password2']  # 使用するフィールド