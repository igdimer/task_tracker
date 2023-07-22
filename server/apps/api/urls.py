from django.urls import include, path

urlpatterns = [
    path('users/', include('server.apps.api.users.urls', namespace='users')),
    path('projects/', include('server.apps.api.projects.urls', namespace='projects')),
    path('issues/', include('server.apps.api.issues.urls', namespace='issues')),
    path('auth/', include('server.apps.api.auth.urls', namespace='auth')),
]
