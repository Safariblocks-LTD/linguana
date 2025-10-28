from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'annotations', views.AnnotationViewSet, basename='annotation')
router.register(r'tasks', views.AnnotationTaskViewSet, basename='annotation-task')
router.register(r'consensus', views.ConsensusResultViewSet, basename='consensus')

urlpatterns = [
    path('', include(router.urls)),
    path('queue/stats/', views.annotation_queue_stats, name='annotation_queue_stats'),
]
