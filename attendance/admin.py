from django.contrib import admin
from .models import ShopConfig, Attendance

# 管理画面にテーブルを登録する
admin.site.register(ShopConfig)
admin.site.register(Attendance)