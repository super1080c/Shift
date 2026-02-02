from django.urls import path
from . import views

urlpatterns = [
    # http://.../attendance/ にアクセスした時の設定
    path('', views.index, name='index'),
]