from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーター
from django.contrib import messages  # フラッシュメッセージを表示するためのモジュール
from django.contrib.auth import get_user_model  # カスタムユーザーモデル対応
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app_video.forms import VideoForm  # 作成したフォームをインポート
from app_video.models import Video  # Videoモデルをインポート
from django.db.models import Q
from app_video.utils import ensure_user_has_default_videos
from django.contrib.auth.decorators import login_required

# Djangoのカスタムユーザー対応（デフォルトのUserモデルを取得）
User = get_user_model()

@login_required
def home(request):
    ensure_user_has_default_videos(request.user)
    return render(request, 'home.html')

@login_required  # ユーザーがログインしていないとアクセスできないようにする

# 動画登録画面を表示するビュー
def video_register(request):
    """
    動画登録ページのビュー
    """
    if request.method == "POST":  # フォームが送信された場合
        form = VideoForm(request.POST)  # フォームのデータを取得
        if form.is_valid():  # バリデーションチェック（入力が正しいか）
            video = form.save(commit=False)  # まだデータベースには保存しない
            # リスト → カンマ区切り文字列に変換
            video.time_category = form.cleaned_data['time_category']
            video.type_category = form.cleaned_data['type_category']
            video.body_part_category = form.cleaned_data['body_part_category']
            video.user = request.user  # 現在ログインしているユーザーを登録

            # MM:SS 形式の時間を秒数に変換
            mm_ss = form.cleaned_data["duration_time"]
            try:
                minutes, seconds = map(int, mm_ss.split(":"))  # MMとSSを分解
                video.duration_seconds = minutes * 60 + seconds  # 秒に変換
                video.save()  # データベースに保存
                return redirect("app_video:video_list")  # 成功後、動画一覧ページにリダイレクト
            except ValueError:  # 例外処理（入力ミスなど）
                messages.error(request, "時間の形式は MM:SS で入力してください。")

    else:  # フォームを開いたとき（GETリクエスト）
        form = VideoForm()

    # フォームをテンプレートに渡して表示
    return render(request, "video_register.html", {"form": form})

# 動画一覧画面を表示するビュー
def video_list(request):
    #  表示するのは「ユーザー自身の動画」のみ（登録 + コピー）
    videos = Video.objects.filter(user=request.user, is_template=False)

    # GETパラメータを取得
    time_categories = request.GET.getlist('time_category')
    type_categories = request.GET.getlist('type_category')
    body_part_categories = request.GET.getlist('body_part_category')
    keyword = request.GET.get('keyword')

    # フィルター条件に合わせて絞り込む
    if time_categories and 'all' not in time_categories:
        q_time = Q()
        for val in time_categories:
            q_time |= Q(time_category__contains=val)
        videos = videos.filter(q_time)

    # 種別フィルタ
    if type_categories and 'all' not in type_categories:
        q_type = Q()
        for val in type_categories:
            q_type |= Q(type_category__contains=val)
        videos = videos.filter(q_type)

    # 部位フィルタ
    if body_part_categories and 'all' not in body_part_categories:
        q_body = Q()
        for val in body_part_categories:
            q_body |= Q(body_part_category__contains=val)
        videos = videos.filter(q_body)

    # キーワード検索
    if keyword:
        videos = videos.filter(
            Q(memo__icontains=keyword) |
            Q(youtuber_name__icontains=keyword) |
            Q(duration_time__icontains=keyword) |
            Q(time_category__icontains=keyword) |
            Q(type_category__icontains=keyword) |
            Q(body_part_category__icontains=keyword)
        )

    #  テンプレート動画は表示されず、コピーされた動画と自分の動画だけ表示
    return render(request, 'video_list.html', {'videos': videos})

# --- 編集画面 ---
def video_edit(request, pk):
    # 編集対象の動画データを取得
    video = get_object_or_404(Video, pk=pk)

    if request.method == 'POST':
        # 保存ボタンを押したとき
        form = VideoForm(request.POST, instance=video)
        if form.is_valid():
            form.save()
            return redirect('app_video:video_list')  # 保存したら一覧に戻る
    else:
        # 最初に開いたとき
        form = VideoForm(instance=video)

    return render(request, 'video_edit.html', {'form': form})

# ✅ 動画削除（自分の動画のみ削除可、共有テンプレートは削除不可）
@csrf_exempt
def video_delete(request, pk):
    if request.method == 'POST':
        video = get_object_or_404(Video, pk=pk)
        print("削除対象:", video.pk, video.user, video.is_template, "ログインユーザー:", request.user)

        # ✅ 共有テンプレートは削除禁止
        if video.is_template and video.user is None:
            print("削除拒否: 共有テンプレート")
            return JsonResponse({'error': '共有テンプレートは削除できません'}, status=403)

        # ✅ 所有者が一致しない動画も削除禁止
        if not video.user or video.user != request.user:
            print("削除拒否: 所有者が一致しません")
            return JsonResponse({'error': 'この動画は削除できません'}, status=403)

        # ✅ 削除実行
        video.delete()
        print("削除成功")
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)
