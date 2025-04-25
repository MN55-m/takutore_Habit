from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーター
from django.contrib import messages  # フラッシュメッセージを表示するためのモジュール
from django.contrib.auth import get_user_model  # カスタムユーザーモデル対応
from app_video.forms import VideoForm  # 作成したフォームをインポート
from app_video.models import Video  # Videoモデルをインポート

# Djangoのカスタムユーザー対応（デフォルトのUserモデルを取得）
User = get_user_model()

@login_required  # ユーザーがログインしていないとアクセスできないようにする
def video_register(request):
    """
    動画登録ページのビュー
    """
    if request.method == "POST":  # フォームが送信された場合
        form = VideoForm(request.POST)  # フォームのデータを取得
        if form.is_valid():  # バリデーションチェック（入力が正しいか）
            video = form.save(commit=False)  # まだデータベースには保存しない
            video.user = request.user  # 現在ログインしているユーザーを登録

            # MM:SS 形式の時間を秒数に変換
            mm_ss = form.cleaned_data["duration_time"]
            try:
                minutes, seconds = map(int, mm_ss.split(":"))  # MMとSSを分解
                video.duration_seconds = minutes * 60 + seconds  # 秒に変換
                video.save()  # データベースに保存
                messages.success(request, "動画を登録しました！")  # 成功メッセージを表示
                return redirect("app_video:video_list")  # 成功後、動画一覧ページにリダイレクト
            except ValueError:  # 例外処理（入力ミスなど）
                messages.error(request, "時間の形式は MM:SS で入力してください。")

    else:  # フォームを開いたとき（GETリクエスト）
        form = VideoForm()
        messages.error(request, "入力内容にエラーがあります。")

    # フォームをテンプレートに渡して表示
    return render(request, "video_register.html", {"form": form})

def video_list(request):
    # ビューのロジック
    return render(request, 'video_list.html')