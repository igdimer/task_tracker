from django.urls import path

from . import views

app_name = 'issues'

urlpatterns = [
    path('create', views.IssueCreateApi.as_view(), name='create'),
]
