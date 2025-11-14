from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


def api_root(request):
    return JsonResponse({
        'service': 'Linguana API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'documentation': '/api/docs/',
            'schema': '/api/schema/',
            'admin': '/admin/',
            'auth': '/api/auth/',
            'audio': '/api/audio/',
            'annotations': '/api/annotations/',
            'rewards': '/api/rewards/',
        },
        'websocket': {
            'asr_streaming': 'ws://127.0.0.1:8000/ws/asr/stream/{dialect}/'
        }
    })


urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/auth/', include('users.urls')),
    path('api/audio/', include('audio.urls')),
    path('api/annotations/', include('annotations.urls')),
    path('api/rewards/', include('rewards.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
