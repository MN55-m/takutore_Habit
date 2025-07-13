from django.shortcuts import render, redirect, get_object_or_404  # HTMLテンプレートのレンダリングとリダイレクト用
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーター
from django.contrib.auth import get_user_model  # カスタムユーザーモデル対応
from app_workout.forms import WorkoutSettingForm, WorkoutMenuForm
from django.utils import timezone  # ← Django標準
from django.contrib import messages
from app_workout.models import WorkoutRecord, WorkoutMenu, Video  # Videoモデルの読み込み
from django.db.models import Q
import itertools  # 組み合わせ計算に使用
from django.utils.timezone import localtime

# Djangoのカスタムユーザー対応（デフォルトのUserモデルを取得）
User = get_user_model()

@login_required  # ユーザーがログインしていないとアクセスできないようにする

# ワークアウト設定ページビュー（ログインが必要）
def workout_settingsView(request):
    if request.method == 'POST':
        form = WorkoutSettingForm(request.POST)
        if form.is_valid():
            duration = form.cleaned_data['duration']
            parts = form.cleaned_data['parts']
            types = form.cleaned_data['types']

            # 🌞🌙 時間帯を日本時間で判定
            now_japan = timezone.localtime(timezone.now())
            hour = now_japan.hour

            if 0 <= hour < 12:
              timing = 'morning'
              timing_display = '朝トレ'
            else:
              timing = 'night'
              timing_display = '夜トレ'

            # ここで timing, duration, parts, types を次画面に渡す or セッションに保存
            request.session['workout_data'] = {
                'duration': duration,
                'parts': parts,
                'types': types,
                'timing': timing,
            }

            return redirect('app_workout:workout_menu')  # 次画面へ
    else:
        form = WorkoutSettingForm()
        # 💡 ここでも日本時間を判定して timing_display を作る！
        now_japan = timezone.localtime(timezone.now())
        hour = now_japan.hour
        if 0 <= hour < 12:
            timing_display = '朝トレ'
        else:
            timing_display = '夜トレ'

    return render(request, 'workout_settings.html', {'form': form, 'timing_display': timing_display,})

# 運動メニューの作成
def workout_menuView(request):
    # 条件入力画面でセッションに保存したデータを取得
    data = request.session.get('workout_data')
    if not data:
        return redirect('app_workout:workout_settings')

    duration_limit = int(data['duration']) * 60
    selected_parts = data['parts']
    selected_types = data['types']
    timing = data['timing']
    time_code = '0' if timing == 'morning' else '1'

    videos = Video.objects.filter(
        Q(user=request.user) | Q(is_template=True),
        time_category__contains=time_code
    )

    if selected_parts:
        videos = videos.filter(
            body_part_category__regex=r'(' + '|'.join(selected_parts) + ')'
        )
    if selected_types:
        videos = videos.filter(
            type_category__regex=r'(' + '|'.join(selected_types) + ')'
        )

    all_videos = list(videos)

    type_order = ["0", "1", "2", "3"]
    body_order = ["0", "1", "2", "3", "4", "5", "6"]

    def video_sort_key(v):
        type_index = next((type_order.index(t) for t in v.type_category.split(",") if t in type_order), 99)
        body_index = next((body_order.index(b) for b in v.body_part_category.split(",") if b in body_order), 99)
        return (type_index, body_index)

    per_part_time = duration_limit // len(selected_parts)
    remaining_time = duration_limit % len(selected_parts)
    selected_videos = []

    for i, part in enumerate(selected_parts):
        part_duration = per_part_time + (1 if i < remaining_time else 0)
        part_videos = [v for v in all_videos if part in v.body_part_category.split(",")]
        part_selected = []

        per_type_time = part_duration // len(selected_types)
        remaining_type_time = part_duration % len(selected_types)

        for j, type_ in enumerate(selected_types):
            time_for_type = per_type_time + (1 if j < remaining_type_time else 0)
            type_videos = [v for v in part_videos if type_ in v.type_category.split(",")]
            type_videos_sorted = sorted(type_videos, key=lambda v: v.duration_seconds or 0, reverse=True)

            total = 0
            for video in type_videos_sorted:
                dur = video.duration_seconds or 0
                if total + dur <= time_for_type:
                    part_selected.append(video)
                    total += dur
                if total >= time_for_type:
                    break

        total_part_time = sum(v.duration_seconds or 0 for v in part_selected)
        if total_part_time < part_duration:
            needed = part_duration - total_part_time
            fallback_videos = sorted(part_videos, key=lambda v: v.duration_seconds or 0, reverse=True)
            total = 0
            for video in fallback_videos:
                dur = video.duration_seconds or 0
                if total + dur <= needed:
                    part_selected.append(video)
                    total += dur
                if total >= needed:
                    break

        selected_videos.extend(part_selected)

    sorted_videos = sorted(selected_videos, key=video_sort_key)
    total_seconds = sum(v.duration_seconds or 0 for v in sorted_videos)

    return render(request, 'workout_menu.html', {
        'videos': sorted_videos,
        'total_time': total_seconds,
        'total_time_minutes': total_seconds // 60,
        'timing_display': '朝トレ' if time_code == '0' else '夜トレ',
    })

def save_workout_menuView(request):
    # 運動条件（セッション）取得
    data = request.session.get('workout_data')
    if not data:
        messages.error(request, "運動条件が見つかりません。")
        return redirect('app_workout:workout_settings')

    # 入力値取得
    duration_limit = int(data['duration']) * 60
    selected_parts = data['parts']
    selected_types = data['types']
    timing = data['timing']
    time_code = '0' if timing == 'morning' else '1'

    # モーダルから入力された値（体重・メモ）を取得
    weight_record = request.POST.get('weight_record') or None
    memo = request.POST.get('memo') or None

    # 対象動画を再取得（前回と同様）
    videos = Video.objects.filter(
        Q(user=request.user) | Q(is_template=True),
        time_category__contains=time_code
    )

    if selected_parts:
        videos = videos.filter(body_part_category__regex=r'(' + '|'.join(selected_parts) + ')')
    if selected_types:
        videos = videos.filter(type_category__regex=r'(' + '|'.join(selected_types) + ')')

    all_videos = list(videos)
    if not all_videos:
        messages.error(request, "条件に合う動画が見つかりませんでした。")
        return redirect('app_workout:workout_settings')

   # 並び順ルール
    type_order = ["0", "1", "2", "3"]
    body_order = ["0", "1", "2", "3", "4", "5", "6"]

    def video_sort_key(v):
        type_index = next((type_order.index(t) for t in v.type_category.split(",") if t in type_order), 99)
        body_index = next((body_order.index(b) for b in v.body_part_category.split(",") if b in body_order), 99)
        return (type_index, body_index)
    
    # 各部位に均等配分 → 各種別にも均等配分
    per_part_time = duration_limit // len(selected_parts)
    remaining_time = duration_limit % len(selected_parts)
    selected_videos = []

    for i, part in enumerate(selected_parts):
        part_duration = per_part_time + (1 if i < remaining_time else 0)
        part_videos = [v for v in all_videos if part in v.body_part_category.split(",")]
        part_selected = []

        per_type_time = part_duration // len(selected_types)
        remaining_type_time = part_duration % len(selected_types)

        for j, type_ in enumerate(selected_types):
            time_for_type = per_type_time + (1 if j < remaining_type_time else 0)
            type_videos = [v for v in part_videos if type_ in v.type_category.split(",")]
            type_videos_sorted = sorted(type_videos, key=lambda v: v.duration_seconds or 0, reverse=True)

            total = 0
            for video in type_videos_sorted:
                dur = video.duration_seconds or 0
                if total + dur <= time_for_type:
                    part_selected.append(video)
                    total += dur
                if total >= time_for_type:
                    break

        total_part_time = sum(v.duration_seconds or 0 for v in part_selected)
        if total_part_time < part_duration:
            needed = part_duration - total_part_time
            fallback_videos = sorted(part_videos, key=lambda v: v.duration_seconds or 0, reverse=True)
            total = 0
            for video in fallback_videos:
                dur = video.duration_seconds or 0
                if total + dur <= needed:
                    part_selected.append(video)
                    total += dur
                if total >= needed:
                    break

        selected_videos.extend(part_selected)

    if not selected_videos:
        messages.error(request, "動画の組み合わせが見つかりませんでした。")
        return redirect('app_workout:workout_settings')

    # 運動記録作成（体重・メモあり）
    workout_record = WorkoutRecord.objects.create(
        user=request.user,
        weight_record=weight_record,
        memo=memo,
        created_at=localtime(timezone.now())
    )

    # 並び順ソート（種別 → 部位）
    sorted_videos = sorted(selected_videos, key=video_sort_key)

    # 運動メニュー保存
    for i, video in enumerate(sorted_videos, start=1):
        WorkoutMenu.objects.create(
            workout_record=workout_record,
            video=video,
            sequence=i
        )

    print("=== WorkoutMenu 保存確認 ===")
    menus = WorkoutMenu.objects.filter(workout_record=workout_record)
    for m in menus:
      print("動画タイトル:", m.video.memo)
      print("部位:", m.video.get_body_part_labels())
      print("種別:", m.video.get_type_labels())
      print("時間:", m.video.duration_time)

    return redirect('app_calendar:calendar')  # カレンダー画面へ（URLは適宜修正）

# WorkoutMenu を追加するためのビュー関数（URLに記録IDを含む）
@login_required  # ログイン必須
def add_workout_menu(request, record_id):
    # 該当の WorkoutRecord を取得（存在しない場合は 404）
    record = get_object_or_404(WorkoutRecord, id=record_id, user=request.user)

    if request.method == 'POST':
        # POST リクエスト時、フォームにデータをバインド
        form = WorkoutMenuForm(request.POST)
        if form.is_valid():
            # 一時保存（commit=False）して、workout_record を手動でセット
            menu = form.save(commit=False)
            menu.workout_record = record
            menu.save()  # 保存
            return redirect('app_calendar:calendar')  # 保存後はカレンダー画面へリダイレクト
    else:
        # GET リクエスト時は空のフォームを表示
        form = WorkoutMenuForm()

    # テンプレートへデータを渡して表示
    return render(request, 'add_workout_menu.html', {
        'form': form,
        'record': record,
    })