from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import math
from .models import Attendance, ShopConfig

# --- 距離計算の関数（ヒュベニの公式という数学を使っています） ---
def calculate_distance(lat1, lon1, lat2, lon2):
    # 地球の半径 (m)
    R = 6371000
    
    # ラジアンに変換
    rad_lat1 = math.radians(lat1)
    rad_lon1 = math.radians(lon1)
    rad_lat2 = math.radians(lat2)
    rad_lon2 = math.radians(lon2)
    
    # 距離計算
    d_lat = rad_lat2 - rad_lat1
    d_lon = rad_lon2 - rad_lon1
    
    a = math.sin(d_lat/2)**2 + math.cos(rad_lat1) * math.cos(rad_lat2) * math.sin(d_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c # 距離 (m)

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

        # 2. 店舗設定を取得
        config = ShopConfig.objects.first()
        if not config:
            messages.error(request, '店舗設定が行われていません。管理画面から設定してください。')
            return redirect('index')

        # 3. ★ここが新機能: 距離チェック
        distance = calculate_distance(latitude, longitude, config.latitude, config.longitude)
        
        # 許容範囲（メートル）。厳しくするなら30、緩くするなら100などに変更可
        LIMIT_DISTANCE = 50 

        if distance > LIMIT_DISTANCE:
            # 距離が遠すぎる場合
            messages.error(request, f'店舗から遠すぎます！ 店までの距離: {int(distance)}m (許容範囲: {LIMIT_DISTANCE}m)')
            return redirect('index')

        # 4. 日付計算
        now = timezone.now()
        today_business_date = get_business_date(now)

        # 5. 保存処理
        if action_type == 'clock_in':
            Attendance.objects.create(
                user=request.user,
                business_date=today_business_date,
                clock_in_at=now,
                status='working'
            )
            messages.success(request, f'出勤しました！（店までの距離: {int(distance)}m）')
        
        elif action_type == 'clock_out':
            attendance = Attendance.objects.filter(
                user=request.user, 
                business_date=today_business_date,
                status='working'
            ).first()
            
            if attendance:
                attendance.clock_out_at = now
                attendance.status = 'finished'
                attendance.save()
                messages.info(request, f'退勤しました。（店までの距離: {int(distance)}m）')
            else:
                messages.error(request, '出勤データが見つかりません。')

        return redirect('index')

    return render(request, 'attendance/index.html')