from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    # トップページ
    path('', views.index, name='index'),
    
    # ログイン画面（さっき作ったHTMLを使うよ、と指定）
    path('login/', LoginView.as_view(template_name='attendance/login.html'), name='login'),
    
    # ログアウト（ログアウトしたらログイン画面に戻る設定）
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
]