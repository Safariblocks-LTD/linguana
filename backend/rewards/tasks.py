from celery import shared_task
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import logging
from .models import Reward, RewardPool, Transaction, WithdrawalRequest
from audio.models import AudioClip
from .blockchain import send_usdc_reward, get_transaction_receipt

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def create_and_distribute_rewards(self, clip_id):
    """Create reward records and distribute USDC for validated clip"""
    try:
        with transaction.atomic():
            clip = AudioClip.objects.select_for_update().get(id=clip_id)
            
            if not clip.consensus_reached or clip.status != 'validated':
                logger.warning(f"Clip {clip_id} is not validated, skipping rewards")
                return
            
            existing_rewards = Reward.objects.filter(clip=clip).exists()
            if existing_rewards:
                logger.info(f"Rewards already created for clip {clip_id}")
                return
            
            total_reward = Decimal(str(settings.DEFAULT_REWARD_AMOUNT_USDC))
            contributor_percentage = Decimal(str(settings.CONTRIBUTOR_REWARD_PERCENTAGE)) / 100
            validator_percentage = Decimal(str(settings.VALIDATOR_REWARD_PERCENTAGE)) / 100
            
            contributor_amount = total_reward * contributor_percentage
            
            annotations = clip.annotations.filter(validated=True)
            validator_count = annotations.count()
            
            if validator_count == 0:
                logger.error(f"No validated annotations found for clip {clip_id}")
                return
            
            validator_amount_each = (total_reward * validator_percentage) / validator_count
            
            contributor_reward = Reward.objects.create(
                clip=clip,
                recipient=clip.uploader,
                reward_type='contributor',
                amount_usdc=contributor_amount,
                status='pending'
            )
            
            validator_rewards = []
            for annotation in annotations:
                validator_reward = Reward.objects.create(
                    clip=clip,
                    recipient=annotation.annotator,
                    reward_type='validator',
                    amount_usdc=validator_amount_each,
                    status='pending'
                )
                validator_rewards.append(validator_reward)
            
            logger.info(f"Created rewards for clip {clip_id}: 1 contributor + {validator_count} validators")
            
            if clip.uploader.wallet_verified and clip.uploader.wallet_address:
                distribute_reward_on_chain.delay(str(contributor_reward.id))
            else:
                credit_user_balance(contributor_reward)
            
            for vr in validator_rewards:
                if vr.recipient.wallet_verified and vr.recipient.wallet_address:
                    distribute_reward_on_chain.delay(str(vr.id))
                else:
                    credit_user_balance(vr)
    
    except AudioClip.DoesNotExist:
        logger.error(f"AudioClip {clip_id} not found")
    except Exception as exc:
        logger.error(f"Error creating rewards for clip {clip_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=120)


def credit_user_balance(reward):
    """Credit user balance for users without wallet"""
    try:
        user = reward.recipient
        user.balance_usdc += reward.amount_usdc
        user.total_earnings_usdc += reward.amount_usdc
        user.save(update_fields=['balance_usdc', 'total_earnings_usdc'])
        
        reward.status = 'completed'
        reward.released = True
        reward.released_at = timezone.now()
        reward.metadata = {'payment_method': 'balance_credit'}
        reward.save()
        
        logger.info(f"Credited ${reward.amount_usdc} to user {user.username} balance")
    except Exception as e:
        logger.error(f"Error crediting user balance for reward {reward.id}: {str(e)}")


@shared_task(bind=True, max_retries=3)
def distribute_reward_on_chain(self, reward_id):
    """Distribute reward via blockchain transaction"""
    try:
        reward = Reward.objects.get(id=reward_id)
        
        if reward.status == 'completed':
            logger.info(f"Reward {reward_id} already completed")
            return
        
        if not reward.recipient.wallet_verified or not reward.recipient.wallet_address:
            logger.warning(f"User {reward.recipient.username} has no verified wallet, crediting balance")
            credit_user_balance(reward)
            return
        
        reward.status = 'processing'
        reward.save()
        
        tx_hash = send_usdc_reward(
            to_address=reward.recipient.wallet_address,
            amount_usdc=float(reward.amount_usdc)
        )
        
        if tx_hash:
            reward.tx_hash = tx_hash
            reward.tx_url = f"https://sepolia.basescan.org/tx/{tx_hash}"
            reward.save()
            
            verify_transaction.delay(str(reward_id), tx_hash)
            
            logger.info(f"Reward {reward_id} transaction sent: {tx_hash}")
        else:
            reward.status = 'failed'
            reward.error_message = 'Failed to send blockchain transaction'
            reward.save()
            
            credit_user_balance(reward)
    
    except Reward.DoesNotExist:
        logger.error(f"Reward {reward_id} not found")
    except Exception as exc:
        logger.error(f"Error distributing reward {reward_id}: {str(exc)}")
        
        try:
            reward = Reward.objects.get(id=reward_id)
            reward.status = 'failed'
            reward.error_message = str(exc)
            reward.save()
        except:
            pass
        
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=5)
def verify_transaction(self, reward_id, tx_hash):
    """Verify blockchain transaction and update reward status"""
    try:
        reward = Reward.objects.get(id=reward_id)
        
        receipt = get_transaction_receipt(tx_hash)
        
        if receipt:
            if receipt.get('status') == 1:
                reward.status = 'completed'
                reward.released = True
                reward.released_at = timezone.now()
                
                user = reward.recipient
                user.total_earnings_usdc += reward.amount_usdc
                user.save(update_fields=['total_earnings_usdc'])
                
                Transaction.objects.create(
                    transaction_type='reward_payout',
                    user=user,
                    reward=reward,
                    amount_usdc=reward.amount_usdc,
                    tx_hash=tx_hash,
                    tx_url=reward.tx_url,
                    from_address=settings.REWARD_CONTRACT_ADDRESS,
                    to_address=user.wallet_address,
                    gas_used=receipt.get('gasUsed'),
                    block_number=receipt.get('blockNumber'),
                    confirmed=True
                )
                
                reward.save()
                
                logger.info(f"Reward {reward_id} verified and completed")
            else:
                reward.status = 'failed'
                reward.error_message = 'Transaction failed on blockchain'
                reward.save()
                
                credit_user_balance(reward)
        else:
            raise Exception("Transaction receipt not available yet")
    
    except Reward.DoesNotExist:
        logger.error(f"Reward {reward_id} not found")
    except Exception as exc:
        logger.error(f"Error verifying transaction for reward {reward_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_withdrawal(self, withdrawal_id):
    """Process approved withdrawal request"""
    try:
        withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id)
        
        if withdrawal.status != 'approved':
            logger.warning(f"Withdrawal {withdrawal_id} is not approved")
            return
        
        user = withdrawal.user
        
        if user.balance_usdc < withdrawal.amount_usdc:
            withdrawal.status = 'rejected'
            withdrawal.admin_notes = 'Insufficient balance'
            withdrawal.save()
            return
        
        withdrawal.status = 'processing'
        withdrawal.save()
        
        tx_hash = send_usdc_reward(
            to_address=withdrawal.wallet_address,
            amount_usdc=float(withdrawal.amount_usdc)
        )
        
        if tx_hash:
            withdrawal.tx_hash = tx_hash
            withdrawal.save()
            
            user.balance_usdc -= withdrawal.amount_usdc
            user.save(update_fields=['balance_usdc'])
            
            verify_withdrawal_transaction.delay(str(withdrawal_id), tx_hash)
            
            logger.info(f"Withdrawal {withdrawal_id} transaction sent: {tx_hash}")
        else:
            withdrawal.status = 'failed'
            withdrawal.save()
    
    except WithdrawalRequest.DoesNotExist:
        logger.error(f"WithdrawalRequest {withdrawal_id} not found")
    except Exception as exc:
        logger.error(f"Error processing withdrawal {withdrawal_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=5)
def verify_withdrawal_transaction(self, withdrawal_id, tx_hash):
    """Verify withdrawal transaction"""
    try:
        withdrawal = WithdrawalRequest.objects.get(id=withdrawal_id)
        
        receipt = get_transaction_receipt(tx_hash)
        
        if receipt:
            if receipt.get('status') == 1:
                withdrawal.status = 'completed'
                withdrawal.processed_at = timezone.now()
                withdrawal.save()
                
                Transaction.objects.create(
                    transaction_type='withdrawal',
                    user=withdrawal.user,
                    amount_usdc=withdrawal.amount_usdc,
                    tx_hash=tx_hash,
                    tx_url=f"https://sepolia.basescan.org/tx/{tx_hash}",
                    from_address=settings.REWARD_CONTRACT_ADDRESS,
                    to_address=withdrawal.wallet_address,
                    gas_used=receipt.get('gasUsed'),
                    block_number=receipt.get('blockNumber'),
                    confirmed=True
                )
                
                logger.info(f"Withdrawal {withdrawal_id} completed")
            else:
                withdrawal.status = 'failed'
                
                user = withdrawal.user
                user.balance_usdc += withdrawal.amount_usdc
                user.save(update_fields=['balance_usdc'])
                
                withdrawal.save()
        else:
            raise Exception("Transaction receipt not available yet")
    
    except WithdrawalRequest.DoesNotExist:
        logger.error(f"WithdrawalRequest {withdrawal_id} not found")
    except Exception as exc:
        logger.error(f"Error verifying withdrawal transaction {withdrawal_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60)
