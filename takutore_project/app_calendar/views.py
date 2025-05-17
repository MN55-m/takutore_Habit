from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーター
from django.contrib.auth import get_user_model  # カスタムユーザーモデル対応
from datetime import date, timedelta
from django.utils import timezone  # ← Django標準
from calendar import monthrange
from django.utils.timezone import localtime
from app_workout.models import WorkoutRecord, WorkoutMenu
from app_video.models import Video

# Djangoのカスタムユーザー対応（デフォルトのUserモデルを取得）
User = get_user_model()

@login_required
def calendar_view(request):
    # 今日の日付
    today = localtime(timezone.now()).date()

    # パラメータから年月取得（なければ今月）
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # 月初日と末日を取得
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # カレンダー表示用に1日～末日までリスト化
    days = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    # 運動記録（この月分）
    records = WorkoutRecord.objects.filter(
        user=request.user,
        created_at__date__range=(first_day, last_day)
    )

    # 日付→記録の辞書（複数でも対応できる構造に）
    record_map = {}
    for rec in records:
        rec_date = localtime(rec.created_at).date()
        if rec_date not in record_map:
            record_map[rec_date] = []
        # 運動記録を追加
        record_map[rec_date].append(rec)

        # ← ここでWorkoutMenuとVideoの内容を表示（デバッグ）
        print("【デバッグ】記録日：", rec_date, "体重：", rec.weight_record)
        for menu in rec.workoutmenu_set.all():
            video = menu.video
            print("  ▶ 動画タイトル：", video.memo)
            print("  - 部位：", video.get_body_part_labels())
            print("  - 種別：", video.get_type_labels())
            print("  - 時間：", video.duration_time)

    # 前月/翌月のリンク用データ
    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month = (last_day + timedelta(days=1)).replace(day=1)

    return render(request, "calendar.html", {
        "year": year,
        "month": month,
        "days": days,
        "record_map": record_map,
        "prev_month": {"year": prev_month.year, "month": prev_month.month},
        "next_month": {"year": next_month.year, "month": next_month.month},
    })

# 編集画面用ビュー
@login_required
def edit_day_view(request, year, month, day):
    target_date = date(year, month, day)
    records = WorkoutRecord.objects.filter(user=request.user, created_at__date=target_date)

    if request.method == 'POST':
        weight = request.POST.get("weight_record")
        memo = request.POST.get("memo")

        if records.exists():
            record = records.first()
            record.weight_record = weight
            record.memo = memo
            record.save()
        else:
            WorkoutRecord.objects.create(
                user=request.user,
                weight_record=weight,
                memo=memo,
                created_at=timezone.now()
            )
        return redirect("app_calendar:calendar")
    
    

    return render(request, "calendar_edit.html", {
        "date": target_date,
        "records": records,
    })

