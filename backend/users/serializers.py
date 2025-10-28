from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Badge, UserBadge


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                try:
                    user_obj = User.objects.get(email=email)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        attrs['user'] = user
        return attrs


class WalletConnectSerializer(serializers.Serializer):
    wallet_address = serializers.CharField(max_length=42)
    signature = serializers.CharField()
    message = serializers.CharField()
    
    def validate_wallet_address(self, value):
        if not value.startswith('0x') or len(value) != 42:
            raise serializers.ValidationError('Invalid Ethereum wallet address.')
        return value.lower()


class FirebaseAuthSerializer(serializers.Serializer):
    firebase_token = serializers.CharField()


class MagicLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ['id', 'name', 'badge_type', 'description', 'icon_url', 'points_reward', 'created_at']


class UserBadgeSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    
    class Meta:
        model = UserBadge
        fields = ['id', 'badge', 'earned_at']


class UserProfileSerializer(serializers.ModelSerializer):
    badges = UserBadgeSerializer(many=True, read_only=True)
    initials = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'role',
            'wallet_address', 'wallet_verified', 'balance_usdc', 'profile_photo_url',
            'nickname', 'bio', 'total_contributions', 'total_validations',
            'total_earnings_usdc', 'streak_days', 'points', 'level',
            'preferred_language', 'badges', 'initials', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'balance_usdc', 'total_contributions', 'total_validations',
            'total_earnings_usdc', 'streak_days', 'points', 'level', 'wallet_verified'
        ]
    
    def get_initials(self, obj):
        return obj.get_initials()


class UserStatsSerializer(serializers.ModelSerializer):
    total_clips_uploaded = serializers.IntegerField(source='total_contributions')
    total_clips_validated = serializers.IntegerField(source='total_validations')
    total_earned = serializers.DecimalField(source='total_earnings_usdc', max_digits=10, decimal_places=2)
    current_streak = serializers.IntegerField(source='streak_days')
    
    class Meta:
        model = User
        fields = [
            'total_clips_uploaded', 'total_clips_validated', 'total_earned',
            'current_streak', 'points', 'level', 'balance_usdc'
        ]
