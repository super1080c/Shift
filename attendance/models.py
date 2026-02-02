from django.db import models
from django.contrib.auth.models import User

# 1. 店舗設定テーブル（GPSや日またぎ時間を管理）
class ShopConfig(models.Model):
    name = models.CharField("店舗名", max_length=100)
    # 店舗のGPS座標（初期値は仮のもの）
    latitude = models.FloatField("店舗の緯度", default=35.6895)
    longitude = models.FloatField("店舗の経度", default=139.6917)
    # ここで「朝5時切り替え」などを設定
    day_change_time = models.TimeField("日付変更時間", default="05:00")

    def __str__(self):
        return self.name

# 2. 勤怠記録テーブル
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="スタッフ")
    business_date = models.DateField("業務日付") # 日またぎ判定後の日付
    clock_in_at = models.DateTimeField("出勤時刻", null=True, blank=True)
    clock_out_at = models.DateTimeField("退勤時刻", null=True, blank=True)
    
    # 勤務状況の管理
    STATUS_CHOICES = [
        ('working', '勤務中'),
        ('finished', '退勤済'),
        ('correction_pending', '修正申請中'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='working')

    def __str__(self):
        return f"{self.user.username} - {self.business_date}"