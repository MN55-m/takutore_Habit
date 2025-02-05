from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.views import View  # クラスベースビューを利用するためのインポート
from app.models import User   # DBモデルをインポート
from django.contrib.auth import login  # ユーザーをログイン状態にするための関数
from django.contrib.auth.mixins import LoginRequiredMixin  # ログインが必要なビューを作成するためのミックスイン

# 動画登録ページビュー（ログインが必要）
class Video_registerView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        return render(request, "video_register.html")

# 動画リストページビュー（ログインが必要）
class Video_listView(LoginRequiredMixin, View):
    login_url = "login"
    def get(self, request):
        return render(request, "video_list.html")
