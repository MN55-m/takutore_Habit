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

            return redirect('workout_menu')  # 次画面へ
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
        # セッションに情報がなければ、条件入力ページへ戻す
        return redirect('workout_settings')

    # 入力されたトレーニング時間（分）を「秒」に変換（合計時間比較用）
    duration_limit = int(data['duration']) * 60

    # 入力された条件を取得
    selected_parts = data['parts']     # 選択された部位（複数可）
    selected_types = data['types']     # 選択された種別（複数可）
    timing = data['timing']            # "morning" or "night"
    time_code = '0' if timing == 'morning' else '1'  # "0":朝トレ, "1":夜トレ

    # 条件に合う動画を取得（ログインユーザーの動画 + テンプレート動画）
    videos = Video.objects.filter(
        Q(user=request.user) | Q(is_template=True),  # 自分の動画 or テンプレート
        time_category__contains=time_code            # 時間帯が一致
    )

    # 部位でフィルタ
    if selected_parts:
        videos = videos.filter(
            body_part_category__regex=r'(' + '|'.join(selected_parts) + ')'
        )

    # 種別でフィルタ
    if selected_types:
        videos = videos.filter(
            type_category__regex=r'(' + '|'.join(selected_types) + ')'
        )

    # 全動画をリスト化（クエリセット → リスト）
    all_videos = list(videos)

    # 希望時間に一番近い組み合わせを探す（絶対差が最小）
    best_combo = []
    smallest_diff = float('inf')  # 初期値：無限大（比較用）

    # 組み合わせの長さ1〜Nまで全て試す（全探索）
    for i in range(1, len(all_videos) + 1):
        for combo in itertools.combinations(all_videos, i):
            total = sum(v.duration_seconds or 0 for v in combo)
            diff = abs(duration_limit - total)
            if diff < smallest_diff:
                best_combo = combo
                smallest_diff = diff
                if diff == 0:
                    break  # ぴったり一致したらそれでOK

    # 選ばれた動画を順番通りに並び替える
    # 順番：トレーニング種別 → 部位（指定の順序で優先度付け）
    type_order = ["0", "1", "2", "3"]  # ストレッチ → 筋トレ → フォームローラー → マッサージ
    body_order = ["0", "1", "2", "3", "4", "5", "6"]  # 姿勢 → 全身 → 脚 → お腹 → 上半身 → 骨盤矯正 → 顔

    # 並び順のルール（最初に一致したカテゴリで判断）
    def video_sort_key(v):
        # type_categoryとbody_part_categoryはカンマ区切りなので、最初に一致したものを使う
        type_index = next((type_order.index(t) for t in v.type_category.split(",") if t in type_order), 99)
        body_index = next((body_order.index(b) for b in v.body_part_category.split(",") if b in body_order), 99)
        return (type_index, body_index)

    # 並び替え実行
    sorted_videos = sorted(best_combo, key=video_sort_key)

    total_seconds = sum(v.duration_seconds or 0 for v in sorted_videos)

    # 結果ページに動画リストを渡す
    return render(request, 'workout_menu.html', {
        'videos': sorted_videos,
        'total_time': total_seconds,
        'total_time_minutes': total_seconds // 60,  # ここで分を計算
        'timing_display': '朝トレ' if time_code == '0' else '夜トレ',
    })

def save_workout_menuView(request):
    # 運動条件（セッション）取得
    data = request.session.get('workout_data')
    if not data:
        messages.error(request, "運動条件が見つかりません。")
        return redirect('workout_settings')

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
    videos = Video.objects.filter(Q(user=request.user) | Q(is_template=True), time_category__contains=time_code)
    if selected_parts:
        videos = videos.filter(body_part_category__regex=r'(' + '|'.join(selected_parts) + ')')
    if selected_types:
        videos = videos.filter(type_category__regex=r'(' + '|'.join(selected_types) + ')')

    all_videos = list(videos)
    best_combo = []
    smallest_diff = float('inf')

    for i in range(1, len(all_videos) + 1):
        for combo in itertools.combinations(all_videos, i):
            total = sum(v.duration_seconds or 0 for v in combo)
            diff = abs(duration_limit - total)
            if diff < smallest_diff:
                best_combo = combo
                smallest_diff = diff
                if diff == 0:
                    break

    if not best_combo:
        messages.error(request, "条件に合う動画が見つかりませんでした。")
        return redirect('workout_settings')

    # 運動記録作成（体重・メモあり）
    workout_record = WorkoutRecord.objects.create(
        user=request.user,
        weight_record=weight_record,
        memo=memo,
        created_at=localtime(timezone.now())
    )

    # 並び順ソート（種別 → 部位）
    type_order = ["0", "1", "2", "3"]
    body_order = ["0", "1", "2", "3", "4", "5", "6"]
    def video_sort_key(v):
        type_index = next((type_order.index(t) for t in v.type_category.split(",") if t in type_order), 99)
        body_index = next((body_order.index(b) for b in v.body_part_category.split(",") if b in body_order), 99)
        return (type_index, body_index)
    sorted_videos = sorted(best_combo, key=video_sort_key)

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

    messages.success(request, "運動履歴を保存しました！")
    return redirect('calendar')  # カレンダー画面へ（URLは適宜修正）

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