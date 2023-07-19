from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup', views.SignUpApi.as_view(), name='signup'),
    path('login', views.LoginApi.as_view(), name='login'),
    path('token-refresh', views.RefreshTokenApi.as_view(), name='token_refresh'),
]
