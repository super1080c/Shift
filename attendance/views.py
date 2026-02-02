from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Attendance

def index(request):
    if request.method == 'POST':
        # 1. フォームから送られたデータを受け取る
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        action_type = request.POST.get('action_type')
        
        # 今日の日付（日またぎ処理は一旦省略してシンプルに）
        today = timezone.now().date()

        # 2. どのボタンが押されたかで分岐
        if action_type == 'clock_in':
            # 出勤処理：新しいデータを作成
            Attendance.objects.create(
                user=request.user,
                business_date=today,
                clock_in_at=timezone.now(),
                status='working'
            )
            messages.success(request, 'おはようございます！出勤しました。')
        
        elif action_type == 'clock_out':
            # 退勤処理：今日の出勤データを探して更新
            # (最新の勤務中のデータを探す)
            attendance = Attendance.objects.filter(
                user=request.user, 
                business_date=today,
                status='working'
            ).first()
            
            if attendance:
                attendance.clock_out_at = timezone.now()
                attendance.status = 'finished'
                attendance.save()
                messages.info(request, 'お疲れ様でした！退勤しました。')
            else:
                messages.error(request, '出勤データが見つかりません。')

        # 処理が終わったらトップページに戻る
        return redirect('index')

    return render(request, 'attendance/index.html')