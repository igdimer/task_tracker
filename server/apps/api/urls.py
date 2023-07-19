from django.urls import include, path

urlpatterns = [
    path('users/', include('server.apps.api.auth.urls', namespace='users')),
]
