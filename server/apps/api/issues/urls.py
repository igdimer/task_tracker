from django.urls import path

from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.IssueListApi.as_view(), name='list'),
    path('create', views.IssueCreateApi.as_view(), name='create'),
    path('<int:issue_id>', views.IssueDetailApi.as_view(), name='detail'),
    path('<int:issue_id>/update', views.IssueUpdateApi.as_view(), name='update'),
]
