from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'clips', views.AudioClipViewSet, basename='audio-clip')
router.register(r'datasets', views.DatasetViewSet, basename='dataset')
router.register(r'benchmarks', views.BenchmarkResultViewSet, basename='benchmark')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/', views.dashboard_stats, name='dashboard_stats'),
]
