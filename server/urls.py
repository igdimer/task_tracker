from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('server.apps.api.urls')),
]

urlpatterns += [
    path('docs/', TemplateView.as_view(  # type: ignore[list-item]
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'},
    ), name='docs'),

]
