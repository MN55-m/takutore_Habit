from django.shortcuts import render, redirect  # HTMLテンプレートのレンダリングとリダイレクト用
from django.contrib.auth.decorators import login_required  # ログイン必須のデコレーター
from django.contrib.auth import get_user_model  # カスタムユーザーモデル対応
from datetime import date, timedelta, datetime
from django.utils import timezone  # ← Django標準
from calendar import monthrange
from django.utils.timezone import localtime
from app_workout.models import WorkoutRecord, WorkoutMenu
from app_video.models import Video
from calendar import Calendar


# Djangoのカスタムユーザー対応（デフォルトのUserモデルを取得）
User = get_user_model()

@login_required
def calendar_view(request):
    calendar = Calendar(firstweekday=6)  # 日曜始まり
    today = localtime(timezone.now()).date()

    # パラメータから年月取得（なければ今月）
    year = int(request.GET.get("year", today.year))
    month = int(request.GET.get("month", today.month))

    # 月初日と末日
    first_day = date(year, month, 1)
    last_day = date(year, month, monthrange(year, month)[1])

    # ✅ 42日分の日付を取得（日曜始まり、他月分含む）
    month_days = list(calendar.itermonthdates(year, month))
    while len(month_days) < 42:
        month_days.append(month_days[-1] + timedelta(days=1))  # 念のため補完

    # days を週ごと（7件）に分割して渡す
    weeks = [month_days[i:i + 7] for i in range(0, len(month_days), 7)]

    # 運動記録の取得（当月内のみ）
    records = WorkoutRecord.objects.filter(
        user=request.user,
        created_at__date__range=(first_day, last_day)
    )

    # 日付 → 複数記録の辞書
    record_map = {}
    for rec in records:
        rec_date = localtime(rec.created_at).date()
        record_map.setdefault(rec_date, []).append(rec)

        # 任意のデバッグ出力
        print("【デバッグ】記録日：", rec_date, "体重：", rec.weight_record)
        for menu in rec.workoutmenu_set.all():
            video = menu.video
            print("  ▶ 動画タイトル：", video.memo)
            print("  - 部位：", video.get_body_part_labels())
            print("  - 種別：", video.get_type_labels())
            print("  - 時間：", video.duration_time)

    # 前月・翌月
    prev_month = (first_day - timedelta(days=1)).replace(day=1)
    next_month = (last_day + timedelta(days=1)).replace(day=1)

    return render(request, "calendar.html", {
        "year": year,
        "month": month,
        "weeks": weeks,  # ← これをテンプレートで使う
        "record_map": record_map,
        "prev_month": {"year": prev_month.year, "month": prev_month.month},
        "next_month": {"year": next_month.year, "month": next_month.month},
        "today": today,
    })


# 編集画面用ビュー
@login_required
def edit_day_view(request, year, month, day, record_id=None):
    target_date = date(year, month, day)

    if record_id:
        # 特定の1レコードのみ編集対象
        records = WorkoutRecord.objects.filter(id=record_id, user=request.user)
    else:
        # 日付で絞り込み（複数ある可能性あり）
        records = WorkoutRecord.objects.filter(user=request.user, created_at__date=target_date).order_by('created_at')

    if request.method == 'POST':
        weight = request.POST.get("weight_record")
        memo = request.POST.get("memo")

        if records.exists():
            # ✅ 最初のレコードだけを更新（それ以外は削除してもよい）
            record = records.first()
            record.weight_record = weight
            record.memo = memo
            record.save()

            # ✅ 重複していた場合、他のレコードを削除する
            if records.count() > 1:
                records.exclude(id=record.id).delete()

        else:
            # ✅ 新規作成：created_at は 0:00 に固定
            created_datetime = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
            WorkoutRecord.objects.create(
                user=request.user,
                weight_record=weight,
                memo=memo,
                created_at=created_datetime
            )

        return redirect("app_calendar:calendar")
        
    return render(request, "calendar_edit.html", {
        "date": target_date,
        "records": records,
    })

