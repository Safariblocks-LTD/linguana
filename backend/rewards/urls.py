from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'rewards', views.RewardViewSet, basename='reward')
router.register(r'pools', views.RewardPoolViewSet, basename='reward-pool')
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'withdrawals', views.WithdrawalRequestViewSet, basename='withdrawal')

urlpatterns = [
    path('', include(router.urls)),
    path('analytics/', views.rewards_analytics, name='rewards_analytics'),
]
