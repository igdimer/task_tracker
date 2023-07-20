from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('create', views.ProjectCreateApi.as_view(), name='create'),
    path('update', views.ProjectUpdateApi.as_view(), name='update'),
    path('<int:project_id>', views.ProjectDetailApi.as_view(), name='detail'),
]
