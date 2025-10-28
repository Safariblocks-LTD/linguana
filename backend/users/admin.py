from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Badge, UserBadge


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'wallet_verified', 'total_contributions', 'total_earnings_usdc', 'level']
    list_filter = ['role', 'wallet_verified', 'is_staff', 'is_active']
    search_fields = ['username', 'email', 'wallet_address']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('role', 'nickname', 'bio', 'profile_photo', 'preferred_language')
        }),
        ('Wallet', {
            'fields': ('wallet_address', 'wallet_verified', 'balance_usdc')
        }),
        ('Stats', {
            'fields': ('total_contributions', 'total_validations', 'total_earnings_usdc', 
                      'streak_days', 'points', 'level')
        }),
        ('Firebase', {
            'fields': ('firebase_uid',)
        }),
    )


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'points_reward', 'created_at']
    search_fields = ['name', 'badge_type']


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge', 'earned_at']
    list_filter = ['badge', 'earned_at']
    search_fields = ['user__username', 'badge__name']
