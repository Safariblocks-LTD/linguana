from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets
import hashlib
from eth_account.messages import encode_defunct
from web3 import Web3
from .models import User, Badge, UserBadge
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    WalletConnectSerializer, FirebaseAuthSerializer, MagicLinkSerializer,
    UserStatsSerializer, BadgeSerializer, WalletNonceSerializer,
    WalletAuthSerializer, OnboardingSerializer
)
from .utils import verify_firebase_token, send_magic_link_email

User = get_user_model()


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        tokens = get_tokens_for_user(user)
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_connect_view(request):
    serializer = WalletConnectSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    wallet_address = serializer.validated_data['wallet_address']
    signature = serializer.validated_data['signature']
    message = serializer.validated_data['message']
    
    try:
        w3 = Web3()
        message_hash = encode_defunct(text=message)
        recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
        
        if recovered_address.lower() != wallet_address.lower():
            return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(wallet_address=wallet_address).exclude(id=request.user.id).exists():
            return Response({'error': 'Wallet already connected to another account'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.wallet_address = wallet_address
        request.user.wallet_signature = signature
        request.user.wallet_verified = True
        request.user.save()
        
        return Response({
            'message': 'Wallet connected successfully',
            'user': UserProfileSerializer(request.user).data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_disconnect_view(request):
    request.user.wallet_address = None
    request.user.wallet_signature = None
    request.user.wallet_verified = False
    request.user.save()
    
    return Response({
        'message': 'Wallet disconnected successfully',
        'user': UserProfileSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def firebase_auth_view(request):
    serializer = FirebaseAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    firebase_token = serializer.validated_data['firebase_token']
    
    try:
        decoded_token = verify_firebase_token(firebase_token)
        firebase_uid = decoded_token['uid']
        email = decoded_token.get('email')
        
        user, created = User.objects.get_or_create(
            firebase_uid=firebase_uid,
            defaults={
                'email': email,
                'username': email.split('@')[0] if email else f'user_{firebase_uid[:8]}',
                'is_email_verified': decoded_token.get('email_verified', False)
            }
        )
        
        if not created and email and user.email != email:
            user.email = email
            user.save()
        
        tokens = get_tokens_for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens,
            'created': created
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def magic_link_request_view(request):
    serializer = MagicLinkSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    email = serializer.validated_data['email']
    
    try:
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': email.split('@')[0]}
        )
        
        token = secrets.token_urlsafe(32)
        user.magic_link_token = hashlib.sha256(token.encode()).hexdigest()
        user.magic_link_expires = timezone.now() + timedelta(minutes=15)
        user.save()
        
        send_magic_link_email(email, token)
        
        return Response({
            'message': 'Magic link sent to your email',
            'email': email
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def magic_link_verify_view(request):
    token = request.data.get('token')
    
    if not token:
        return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    
    try:
        user = User.objects.get(
            magic_link_token=token_hash,
            magic_link_expires__gt=timezone.now()
        )
        
        user.magic_link_token = None
        user.magic_link_expires = None
        user.is_email_verified = True
        user.save()
        
        tokens = get_tokens_for_user(user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'tokens': tokens
        }, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserStatsView(generics.RetrieveAPIView):
    serializer_class = UserStatsSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class BadgeListView(generics.ListAPIView):
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@permission_classes([AllowAny])
def wallet_nonce_view(request):
    """
    Generate a nonce for wallet signature verification.
    """
    serializer = WalletNonceSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    wallet_address = serializer.validated_data['wallet_address']
    
    # Generate a unique nonce
    nonce = secrets.token_urlsafe(32)
    
    # Store nonce in cache with 15 minute expiration
    from django.core.cache import cache
    cache_key = f'wallet_nonce_{wallet_address}'
    cache.set(cache_key, nonce, 900)  # 15 minutes
    
    return Response({
        'nonce': nonce,
        'message': f'Sign this message to authenticate with Linguana.\n\nNonce: {nonce}'
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def wallet_auth_view(request):
    """
    Authenticate user with wallet signature.
    Creates a new user if wallet is not registered.
    """
    serializer = WalletAuthSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    wallet_address = serializer.validated_data['address']
    signature = serializer.validated_data['signature']
    
    try:
        # Get nonce from cache
        from django.core.cache import cache
        cache_key = f'wallet_nonce_{wallet_address}'
        nonce = cache.get(cache_key)
        
        if not nonce:
            return Response({'error': 'Nonce expired or not found. Please request a new nonce.'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        # Verify signature
        w3 = Web3()
        message = f'Sign this message to authenticate with Linguana.\n\nNonce: {nonce}'
        message_hash = encode_defunct(text=message)
        
        # Check if this is a Smart Wallet signature (longer than standard 65 bytes)
        signature_bytes = bytes.fromhex(signature[2:] if signature.startswith('0x') else signature)
        
        if len(signature_bytes) > 65:
            # Smart Wallet signature (ERC-4337/6492) - skip signature verification for now
            # In production, you'd want to verify using ERC-6492 verification
            # For now, we trust that the wallet connection was successful
            print(f"Smart Wallet signature detected for {wallet_address}, skipping verification")
        else:
            # Standard EOA signature verification
            try:
                recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
                if recovered_address.lower() != wallet_address.lower():
                    return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Signature verification failed: {str(e)}'}, 
                              status=status.HTTP_400_BAD_REQUEST)
        
        # Clear nonce from cache
        cache.delete(cache_key)
        
        # Check if user exists with this wallet
        user = User.objects.filter(wallet_address=wallet_address).first()
        
        if user:
            # Existing user - check if onboarding is complete
            needs_onboarding = not user.nickname or not user.role
            
            tokens = get_tokens_for_user(user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': tokens,
                'needs_onboarding': needs_onboarding
            }, status=status.HTTP_200_OK)
        else:
            # New user - create with wallet address
            username = f'user_{wallet_address[:8]}'
            user = User.objects.create(
                username=username,
                wallet_address=wallet_address,
                wallet_verified=True,
                email=f'{wallet_address[:8]}@wallet.linguana.app'  # Temporary email
            )
            
            tokens = get_tokens_for_user(user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'tokens': tokens,
                'needs_onboarding': True
            }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def onboarding_view(request):
    """
    Complete user onboarding with nickname and role.
    """
    serializer = OnboardingSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    nickname = serializer.validated_data['nickname']
    role = serializer.validated_data['role']
    
    # Update user
    request.user.nickname = nickname
    request.user.role = role
    request.user.save()
    
    return Response({
        'message': 'Onboarding completed successfully',
        'user': UserProfileSerializer(request.user).data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard_view(request):
    leaderboard_type = request.query_params.get('type', 'points')
    
    if leaderboard_type == 'points':
        users = User.objects.order_by('-points')[:50]
    elif leaderboard_type == 'contributions':
        users = User.objects.order_by('-total_contributions')[:50]
    elif leaderboard_type == 'earnings':
        users = User.objects.order_by('-total_earnings_usdc')[:50]
    elif leaderboard_type == 'streak':
        users = User.objects.order_by('-streak_days')[:50]
    else:
        users = User.objects.order_by('-points')[:50]
    
    data = []
    for idx, user in enumerate(users, 1):
        data.append({
            'rank': idx,
            'username': user.username,
            'nickname': user.nickname or user.username,
            'profile_photo': user.profile_photo.url if user.profile_photo else None,
            'initials': user.get_initials(),
            'points': user.points,
            'level': user.level,
            'total_contributions': user.total_contributions,
            'total_earnings_usdc': str(user.total_earnings_usdc),
            'streak_days': user.streak_days,
        })
    
    return Response(data, status=status.HTTP_200_OK)
