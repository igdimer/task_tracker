from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('create', views.ProjectCreateApi.as_view(), name='create'),
    path('<int:project_id>', views.ProjectDetailApi.as_view(), name='detail'),
    path('<int:project_id>/update', views.ProjectUpdateApi.as_view(), name='update'),

    path(
        '<int:project_id>/releases/create',
        views.ReleaseCreateApi.as_view(),
        name='release_create',
    ),
    path(
        '<int:project_id>/releases/<int:release_id>',
        views.ReleaseDetailApi.as_view(),
        name='release_detail',
    ),
    path(
        '<int:project_id>/releases/<int:release_id>/update',
        views.ReleaseUpdateApi.as_view(),
        name='release_update',
    ),
]
