from django.db import models
from django.conf import settings
from audio.models import AudioClip
import uuid


class Reward(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    REWARD_TYPE_CHOICES = [
        ('contributor', 'Contributor'),
        ('validator', 'Validator'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    clip = models.ForeignKey(AudioClip, on_delete=models.CASCADE, related_name='rewards')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='rewards')
    reward_type = models.CharField(max_length=20, choices=REWARD_TYPE_CHOICES)
    amount_usdc = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=66, blank=True, null=True)
    tx_url = models.URLField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    released = models.BooleanField(default=False)
    released_at = models.DateTimeField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rewards'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'status']),
            models.Index(fields=['clip', 'reward_type']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.reward_type} reward for {self.recipient.username} - ${self.amount_usdc}"


class RewardPool(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    total_funded_usdc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_distributed_usdc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_balance_usdc = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    wallet_address = models.CharField(max_length=42)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reward_pools'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - ${self.remaining_balance_usdc} remaining"
    
    def add_funds(self, amount):
        self.total_funded_usdc += amount
        self.remaining_balance_usdc += amount
        self.save(update_fields=['total_funded_usdc', 'remaining_balance_usdc', 'updated_at'])
    
    def deduct_funds(self, amount):
        if self.remaining_balance_usdc >= amount:
            self.total_distributed_usdc += amount
            self.remaining_balance_usdc -= amount
            self.save(update_fields=['total_distributed_usdc', 'remaining_balance_usdc', 'updated_at'])
            return True
        return False


class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('reward_payout', 'Reward Payout'),
        ('pool_funding', 'Pool Funding'),
        ('withdrawal', 'Withdrawal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions')
    reward = models.ForeignKey(Reward, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    amount_usdc = models.DecimalField(max_digits=10, decimal_places=2)
    tx_hash = models.CharField(max_length=66)
    tx_url = models.URLField()
    from_address = models.CharField(max_length=42)
    to_address = models.CharField(max_length=42)
    gas_used = models.BigIntegerField(blank=True, null=True)
    gas_price = models.BigIntegerField(blank=True, null=True)
    block_number = models.BigIntegerField(blank=True, null=True)
    confirmed = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['tx_hash']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type} - {self.tx_hash[:10]}..."


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount_usdc = models.DecimalField(max_digits=10, decimal_places=2)
    wallet_address = models.CharField(max_length=42)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tx_hash = models.CharField(max_length=66, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_withdrawals'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        db_table = 'withdrawal_requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Withdrawal ${self.amount_usdc} for {self.user.username} - {self.status}"
