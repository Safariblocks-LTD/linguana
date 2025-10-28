from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum
from .models import Reward, RewardPool, Transaction, WithdrawalRequest
from .serializers import (
    RewardSerializer, RewardPoolSerializer, TransactionSerializer,
    WithdrawalRequestSerializer, WithdrawalRequestCreateSerializer
)
import logging

logger = logging.getLogger(__name__)


class RewardViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['recipient', 'reward_type', 'status', 'released']
    ordering_fields = ['amount_usdc', 'created_at', 'released_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(recipient=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_rewards(self, request):
        queryset = self.get_queryset().filter(recipient=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        user = request.user
        
        total_earned = Reward.objects.filter(
            recipient=user,
            released=True
        ).aggregate(total=Sum('amount_usdc'))['total'] or 0
        
        pending_rewards = Reward.objects.filter(
            recipient=user,
            status='pending'
        ).aggregate(total=Sum('amount_usdc'))['total'] or 0
        
        contributor_earnings = Reward.objects.filter(
            recipient=user,
            reward_type='contributor',
            released=True
        ).aggregate(total=Sum('amount_usdc'))['total'] or 0
        
        validator_earnings = Reward.objects.filter(
            recipient=user,
            reward_type='validator',
            released=True
        ).aggregate(total=Sum('amount_usdc'))['total'] or 0
        
        return Response({
            'total_earned': str(total_earned),
            'pending_rewards': str(pending_rewards),
            'current_balance': str(user.balance_usdc),
            'contributor_earnings': str(contributor_earnings),
            'validator_earnings': str(validator_earnings),
        })


class RewardPoolViewSet(viewsets.ModelViewSet):
    queryset = RewardPool.objects.all()
    serializer_class = RewardPoolSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_active']
    ordering_fields = ['remaining_balance_usdc', 'created_at']
    ordering = ['-created_at']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'fund']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def fund(self, request, pk=None):
        pool = self.get_object()
        amount = request.data.get('amount')
        
        if not amount or float(amount) <= 0:
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        pool.add_funds(float(amount))
        
        return Response({
            'message': f'Pool funded with ${amount}',
            'pool': self.get_serializer(pool).data
        })


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['user', 'transaction_type', 'confirmed']
    ordering_fields = ['amount_usdc', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def my_transactions(self, request):
        queryset = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class WithdrawalRequestViewSet(viewsets.ModelViewSet):
    queryset = WithdrawalRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering_fields = ['amount_usdc', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WithdrawalRequestCreateSerializer
        return WithdrawalRequestSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            return Response(
                {'error': 'Withdrawal request is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        withdrawal.status = 'approved'
        withdrawal.processed_by = request.user
        withdrawal.save()
        
        from .tasks import process_withdrawal
        process_withdrawal.delay(str(withdrawal.id))
        
        return Response({
            'message': 'Withdrawal approved and processing',
            'withdrawal': self.get_serializer(withdrawal).data
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def reject(self, request, pk=None):
        withdrawal = self.get_object()
        
        if withdrawal.status != 'pending':
            return Response(
                {'error': 'Withdrawal request is not pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        withdrawal.status = 'rejected'
        withdrawal.processed_by = request.user
        withdrawal.admin_notes = request.data.get('notes', '')
        withdrawal.save()
        
        return Response({
            'message': 'Withdrawal rejected',
            'withdrawal': self.get_serializer(withdrawal).data
        })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def rewards_analytics(request):
    total_rewards = Reward.objects.count()
    total_distributed = Reward.objects.filter(released=True).aggregate(
        total=Sum('amount_usdc')
    )['total'] or 0
    
    pending_rewards = Reward.objects.filter(status='pending').aggregate(
        total=Sum('amount_usdc')
    )['total'] or 0
    
    contributor_rewards = Reward.objects.filter(
        reward_type='contributor',
        released=True
    ).aggregate(total=Sum('amount_usdc'))['total'] or 0
    
    validator_rewards = Reward.objects.filter(
        reward_type='validator',
        released=True
    ).aggregate(total=Sum('amount_usdc'))['total'] or 0
    
    active_pools = RewardPool.objects.filter(is_active=True)
    total_pool_balance = active_pools.aggregate(
        total=Sum('remaining_balance_usdc')
    )['total'] or 0
    
    analytics = {
        'total_rewards_issued': total_rewards,
        'total_distributed_usdc': str(total_distributed),
        'pending_rewards_usdc': str(pending_rewards),
        'contributor_rewards_usdc': str(contributor_rewards),
        'validator_rewards_usdc': str(validator_rewards),
        'total_pool_balance_usdc': str(total_pool_balance),
        'active_pools_count': active_pools.count(),
    }
    
    return Response(analytics)
