import { useState, useCallback, useEffect } from 'react';
import { api } from '@/lib/api';
import { useAppStore } from '@/stores/useAppStore';

declare global {
  interface Window {
    ethereum?: any;
  }
}

export function useWallet() {
  const { user, setUser } = useAppStore();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [address, setAddress] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (user?.wallet_address) {
      setAddress(user.wallet_address);
      setIsConnected(true);
    }
  }, [user]);

  const connectWallet = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      if (!window.ethereum) {
        throw new Error('Please install MetaMask or Coinbase Wallet');
      }

      // Request account access
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });

      const walletAddress = accounts[0];
      setAddress(walletAddress);

      // Get nonce from backend
      const { nonce } = await api.walletNonce(walletAddress);

      // Sign message
      const message = `Sign this message to authenticate with Linguana.\n\nNonce: ${nonce}`;
      const signature = await window.ethereum.request({
        method: 'personal_sign',
        params: [message, walletAddress],
      });

      // Connect wallet on backend
      const response = await api.walletConnect({
        address: walletAddress,
        signature,
      });

      setUser(response.user);
      setIsConnected(true);

      return response;
    } catch (err: any) {
      const errorMsg = err.message || 'Failed to connect wallet';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, [setUser]);

  const disconnectWallet = useCallback(() => {
    setAddress(null);
    setIsConnected(false);
  }, []);

  const switchNetwork = useCallback(async (chainId: string) => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId }],
      });
    } catch (switchError: any) {
      // Chain not added, try to add it
      if (switchError.code === 4902) {
        try {
          await window.ethereum.request({
            method: 'wallet_addEthereumChain',
            params: [
              {
                chainId,
                chainName: 'Base Sepolia',
                nativeCurrency: {
                  name: 'ETH',
                  symbol: 'ETH',
                  decimals: 18,
                },
                rpcUrls: ['https://sepolia.base.org'],
                blockExplorerUrls: ['https://sepolia.basescan.org'],
              },
            ],
          });
        } catch (addError) {
          throw new Error('Failed to add network');
        }
      } else {
        throw switchError;
      }
    }
  }, []);

  return {
    address,
    isConnected,
    loading,
    error,
    connectWallet,
    disconnectWallet,
    switchNetwork,
  };
}
