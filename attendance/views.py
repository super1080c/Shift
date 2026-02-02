from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
import math
from .models import Attendance, ShopConfig

# --- 距離計算関数 ---
def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    rad_lat1 = math.radians(lat1)
    rad_lon1 = math.radians(lon1)
    rad_lat2 = math.radians(lat2)
    rad_lon2 = math.radians(lon2)
    d_lat = rad_lat2 - rad_lat1
    d_lon = rad_lon2 - rad_lon1
    a = math.sin(d_lat/2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# --- 営業日計算関数 ---
def get_business_date(current_time):
    config = ShopConfig.objects.first()
    if config:
        change_time = config.day_change_time
    else:
        from datetime import time
        change_time = time(5, 0, 0)

    if current_time.time() < change_time:
        return current_time.date() - timedelta(days=1)
    else:
        return current_time.date()

# --- メイン画面処理 ---
@login_required
def index(request):
    if request.method == 'POST':
        # 1. データの取得
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
        except (TypeError, ValueError):
            messages.error(request, '位置情報が取得できませんでした。')
            return redirect('index')
            
        action_type = request.POST.get('action_type')

        # 2. 店舗設定チェック
        config = ShopConfig.objects.first()
        if not config:
            messages.error(request, '店舗設定が行われていません。')
            return redirect('index')

        # 3. 距離チェック
        distance = calculate_distance(latitude, longitude, config.latitude, config.longitude)
        LIMIT_DISTANCE = 50 

        if distance > LIMIT_DISTANCE:
            messages.error(request, f'店舗から遠すぎます！ 距離: {int(distance)}m')
            return redirect('index')

        # 4. 日付・保存処理
        now = timezone.now()
        today_business_date = get_business_date(now)
# --- 分岐処理 ---
        if action_type == 'clock_in':
            Attendance.objects.create(
                user=request.user,
                business_date=today_business_date,
                clock_in_at=now,
                status='working'
            )
            messages.success(request, '出勤しました！')
        
        elif action_type == 'clock_out':
            # 「勤務中」または「休憩中」のデータを探して退勤にする
            attendance = Attendance.objects.filter(
                user=request.user, 
                business_date=today_business_date,
                status__in=['working', 'on_break'] # どちらの状態でも退勤可能に
            ).first()
            
            if attendance:
                attendance.clock_out_at = now
                attendance.status = 'finished'
                attendance.save()
                messages.info(request, 'お疲れ様でした！退勤しました。')
            else:
                messages.error(request, '出勤データが見つかりません。')

        elif action_type == 'break_start':
            # 「勤務中」のデータを探して休憩にする
            attendance = Attendance.objects.filter(
                user=request.user,
                business_date=today_business_date,
                status='working'
            ).first()
            
            if attendance:
                attendance.break_start_at = now
                attendance.status = 'on_break' # ステータス変更
                attendance.save()
                messages.info(request, '休憩に入ります。')
            else:
                messages.error(request, '勤務中のデータが見つかりません。')

        elif action_type == 'break_end':
            # 「休憩中」のデータを探して勤務に戻す
            attendance = Attendance.objects.filter(
                user=request.user,
                business_date=today_business_date,
                status='on_break'
            ).first()
            
            if attendance:
                attendance.break_end_at = now
                attendance.status = 'working' # ステータス戻す
                attendance.save()
                messages.success(request, '休憩から戻りました。業務再開！')
            else:
                messages.error(request, '休憩中のデータが見つかりません。')

        return redirect('index')

    records = Attendance.objects.filter(user=request.user).order_by('-business_date', '-clock_in_at')[:10]
    return render(request, 'attendance/index.html', {'records': records})