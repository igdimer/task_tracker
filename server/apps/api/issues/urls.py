from django.urls import path

from . import views

app_name = 'issues'

urlpatterns = [
    path('', views.IssueListApi.as_view(), name='list'),
    path('create', views.IssueCreateApi.as_view(), name='create'),
    path('<int:issue_id>', views.IssueDetailApi.as_view(), name='detail'),
    path('<int:issue_id>/update', views.IssueUpdateApi.as_view(), name='update'),
    path(
        '<int:issue_id>/comments',
        views.CommentListApi.as_view(),
        name='comments_list',
    ),
    path(
        '<int:issue_id>/comments/create',
        views.CommentCreateApi.as_view(),
        name='comments_create',
    ),
    path(
        '<int:issue_id>/comments/<int:comment_id>',
        views.CommentDetailApi.as_view(),
        name='comments_detail',
    ),
    path(
        '<int:issue_id>/comments/<int:comment_id>/update',
        views.CommentUpdateApi.as_view(),
        name='comments_update',
    ),
]
