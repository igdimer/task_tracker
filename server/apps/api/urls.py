from django.urls import include, path

urlpatterns = [
    path('users/', include('server.apps.api.users.urls', namespace='users')),
]
