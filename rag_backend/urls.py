from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    # OpenAPI schema and Swagger UI
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    # apps
    path('', include('users.urls')),
    path('', include('rag.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
