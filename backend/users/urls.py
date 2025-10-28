from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('wallet/connect/', views.wallet_connect_view, name='wallet_connect'),
    path('wallet/disconnect/', views.wallet_disconnect_view, name='wallet_disconnect'),
    path('firebase/', views.firebase_auth_view, name='firebase_auth'),
    path('magic-link/request/', views.magic_link_request_view, name='magic_link_request'),
    path('magic-link/verify/', views.magic_link_verify_view, name='magic_link_verify'),
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('stats/', views.UserStatsView.as_view(), name='user_stats'),
    path('badges/', views.BadgeListView.as_view(), name='badges'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]
