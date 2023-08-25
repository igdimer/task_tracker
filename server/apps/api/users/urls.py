from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path('create', views.UserCreateApi.as_view(), name='create'),
    path('my_issues', views.UserGetAssignedIssuesApi.as_view(), name='my_issues'),
    path('<int:user_id>', views.UserDetailApi.as_view(), name='detail'),
    path('<int:user_id>/update', views.UserUpdateApi.as_view(), name='update'),
]
