from django.urls import path

from . import views

app_name = 'auth'

urlpatterns = [
    path('login', views.LoginApi.as_view(), name='login'),
    path('token-refresh', views.RefreshTokenApi.as_view(), name='token_refresh'),
]
