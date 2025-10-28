from rest_framework import serializers
from .models import Reward, RewardPool, Transaction, WithdrawalRequest
from users.serializers import UserProfileSerializer
from audio.serializers import AudioClipListSerializer


class RewardSerializer(serializers.ModelSerializer):
    recipient_info = UserProfileSerializer(source='recipient', read_only=True)
    clip_info = AudioClipListSerializer(source='clip', read_only=True)
    
    class Meta:
        model = Reward
        fields = [
            'id', 'clip', 'clip_info', 'recipient', 'recipient_info',
            'reward_type', 'amount_usdc', 'status', 'tx_hash', 'tx_url',
            'error_message', 'released', 'released_at', 'metadata',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'recipient', 'status', 'tx_hash', 'tx_url', 'released', 'released_at'
        ]


class RewardPoolSerializer(serializers.ModelSerializer):
    created_by_info = UserProfileSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = RewardPool
        fields = [
            'id', 'name', 'description', 'total_funded_usdc',
            'total_distributed_usdc', 'remaining_balance_usdc',
            'wallet_address', 'is_active', 'created_by', 'created_by_info',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'total_funded_usdc', 'total_distributed_usdc',
            'remaining_balance_usdc', 'created_by'
        ]


class TransactionSerializer(serializers.ModelSerializer):
    user_info = UserProfileSerializer(source='user', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_type', 'user', 'user_info', 'reward',
            'amount_usdc', 'tx_hash', 'tx_url', 'from_address', 'to_address',
            'gas_used', 'gas_price', 'block_number', 'confirmed',
            'metadata', 'created_at'
        ]


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    user_info = UserProfileSerializer(source='user', read_only=True)
    processed_by_info = UserProfileSerializer(source='processed_by', read_only=True)
    
    class Meta:
        model = WithdrawalRequest
        fields = [
            'id', 'user', 'user_info', 'amount_usdc', 'wallet_address',
            'status', 'tx_hash', 'admin_notes', 'processed_by',
            'processed_by_info', 'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = [
            'user', 'status', 'tx_hash', 'processed_by', 'processed_at'
        ]


class WithdrawalRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = ['amount_usdc', 'wallet_address']
    
    def validate_amount_usdc(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        
        user = self.context['request'].user
        if value > user.balance_usdc:
            raise serializers.ValidationError(
                f"Insufficient balance. Available: ${user.balance_usdc}"
            )
        
        return value
    
    def validate_wallet_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError("Invalid Ethereum wallet address")
        return value.lower()
