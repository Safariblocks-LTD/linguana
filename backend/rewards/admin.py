from django.contrib import admin
from .models import Reward, RewardPool, Transaction, WithdrawalRequest


@admin.register(Reward)
class RewardAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipient', 'reward_type', 'amount_usdc', 'status', 'released', 'created_at']
    list_filter = ['reward_type', 'status', 'released', 'created_at']
    search_fields = ['id', 'recipient__username', 'clip__id', 'tx_hash']
    readonly_fields = ['id', 'created_at', 'updated_at', 'released_at']
    
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'clip', 'recipient', 'reward_type', 'amount_usdc')
        }),
        ('Status', {
            'fields': ('status', 'released', 'released_at')
        }),
        ('Blockchain', {
            'fields': ('tx_hash', 'tx_url', 'error_message')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at', 'updated_at')
        }),
    )


@admin.register(RewardPool)
class RewardPoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'total_funded_usdc', 'total_distributed_usdc', 'remaining_balance_usdc', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'wallet_address']
    readonly_fields = ['total_funded_usdc', 'total_distributed_usdc', 'remaining_balance_usdc', 'created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'transaction_type', 'user', 'amount_usdc', 'confirmed', 'created_at']
    list_filter = ['transaction_type', 'confirmed', 'created_at']
    search_fields = ['id', 'user__username', 'tx_hash']
    readonly_fields = ['id', 'created_at']


@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount_usdc', 'status', 'created_at', 'processed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'user__username', 'wallet_address', 'tx_hash']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']
    
    fieldsets = (
        ('Request Info', {
            'fields': ('id', 'user', 'amount_usdc', 'wallet_address')
        }),
        ('Status', {
            'fields': ('status', 'tx_hash', 'admin_notes')
        }),
        ('Processing', {
            'fields': ('processed_by', 'created_at', 'updated_at', 'processed_at')
        }),
    )
