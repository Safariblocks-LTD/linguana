from web3 import Web3
from eth_account import Account
from django.conf import settings
import logging
import time

logger = logging.getLogger(__name__)


def get_web3_instance():
    """Get Web3 instance connected to Base L2"""
    w3 = Web3(Web3.HTTPProvider(settings.BASE_RPC_URL))
    return w3


def send_usdc_reward(to_address, amount_usdc):
    """Send USDC reward to recipient address on Base L2"""
    try:
        if not settings.REWARD_PRIVATE_KEY or not settings.REWARD_CONTRACT_ADDRESS:
            logger.warning("Blockchain configuration not set, skipping on-chain transaction")
            return None
        
        w3 = get_web3_instance()
        
        if not w3.is_connected():
            logger.error("Failed to connect to Base RPC")
            return None
        
        account = Account.from_key(settings.REWARD_PRIVATE_KEY)
        
        usdc_decimals = 6
        amount_in_wei = int(amount_usdc * (10 ** usdc_decimals))
        
        usdc_abi = [
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"}
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function"
            }
        ]
        
        usdc_contract_address = Web3.to_checksum_address(settings.REWARD_CONTRACT_ADDRESS)
        usdc_contract = w3.eth.contract(address=usdc_contract_address, abi=usdc_abi)
        
        nonce = w3.eth.get_transaction_count(account.address)
        
        gas_price = w3.eth.gas_price
        
        transaction = usdc_contract.functions.transfer(
            Web3.to_checksum_address(to_address),
            amount_in_wei
        ).build_transaction({
            'chainId': settings.BASE_CHAIN_ID,
            'gas': 100000,
            'gasPrice': gas_price,
            'nonce': nonce,
        })
        
        signed_txn = w3.eth.account.sign_transaction(transaction, settings.REWARD_PRIVATE_KEY)
        
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        tx_hash_hex = w3.to_hex(tx_hash)
        
        logger.info(f"USDC transfer transaction sent: {tx_hash_hex}")
        
        return tx_hash_hex
    
    except Exception as e:
        logger.error(f"Error sending USDC reward: {str(e)}")
        return None


def get_transaction_receipt(tx_hash, max_retries=10):
    """Get transaction receipt from blockchain"""
    try:
        w3 = get_web3_instance()
        
        if not w3.is_connected():
            logger.error("Failed to connect to Base RPC")
            return None
        
        for i in range(max_retries):
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                
                return {
                    'status': receipt['status'],
                    'blockNumber': receipt['blockNumber'],
                    'gasUsed': receipt['gasUsed'],
                    'transactionHash': receipt['transactionHash'].hex(),
                }
            except Exception:
                if i < max_retries - 1:
                    time.sleep(3)
                    continue
                else:
                    return None
        
        return None
    
    except Exception as e:
        logger.error(f"Error getting transaction receipt: {str(e)}")
        return None


def get_usdc_balance(address):
    """Get USDC balance for an address"""
    try:
        if not settings.REWARD_CONTRACT_ADDRESS:
            return 0
        
        w3 = get_web3_instance()
        
        if not w3.is_connected():
            logger.error("Failed to connect to Base RPC")
            return 0
        
        usdc_abi = [
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function"
            }
        ]
        
        usdc_contract_address = Web3.to_checksum_address(settings.REWARD_CONTRACT_ADDRESS)
        usdc_contract = w3.eth.contract(address=usdc_contract_address, abi=usdc_abi)
        
        balance_wei = usdc_contract.functions.balanceOf(
            Web3.to_checksum_address(address)
        ).call()
        
        usdc_decimals = 6
        balance_usdc = balance_wei / (10 ** usdc_decimals)
        
        return balance_usdc
    
    except Exception as e:
        logger.error(f"Error getting USDC balance: {str(e)}")
        return 0


def verify_wallet_signature(address, message, signature):
    """Verify wallet signature for authentication"""
    try:
        w3 = get_web3_instance()
        
        from eth_account.messages import encode_defunct
        message_hash = encode_defunct(text=message)
        
        recovered_address = w3.eth.account.recover_message(message_hash, signature=signature)
        
        return recovered_address.lower() == address.lower()
    
    except Exception as e:
        logger.error(f"Error verifying wallet signature: {str(e)}")
        return False
