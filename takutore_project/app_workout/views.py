from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.views import View  # クラスベースビューを利用するためのインポート
from app.models import User   # DBモデルをインポート
from django.contrib.auth import login  # ユーザーをログイン状態にするための関数
from django.contrib.auth.mixins import LoginRequiredMixin  # ログインが必要なビューを作成するためのミックスイン

# ワークアウト設定ページビュー（ログインが必要）
class Workout_settingsView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        return render(request, "workout_settings.html")
