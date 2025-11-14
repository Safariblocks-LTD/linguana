import { useState, useCallback } from 'react';
import { CoinbaseWalletSDK } from '@coinbase/wallet-sdk';
import axios from 'axios';
import { BASE_SEPOLIA_CHAIN_ID, projectId } from '@/lib/wagmi';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface User {
  id: number;
  username: string;
  email: string;
  wallet_address: string;
  wallet_verified: boolean;
  nickname?: string;
  role?: string;
  balance_usdc: string;
  total_contributions: number;
  total_validations: number;
  total_earnings_usdc: string;
  streak_days: number;
  points: number;
  level: number;
}

interface WalletAuthResponse {
  user: User;
  tokens: {
    access: string;
    refresh: string;
  };
  needs_onboarding: boolean;
}

export function useWalletAuth() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const connectWallet = useCallback(async (method: 'reown' | 'base' | 'coinbase'): Promise<WalletAuthResponse> => {
    console.log('[useWalletAuth] Starting connection with method:', method);
    setLoading(true);
    setError(null);

    try {
      let walletAddress: string;
      let signature: string;

      if (method === 'reown') {
        console.log('[useWalletAuth] Initializing WalletConnect...');
        // Use WalletConnect v2 directly
        const { EthereumProvider } = await import('@walletconnect/ethereum-provider');
        
        const provider = await EthereumProvider.init({
          projectId,
          chains: [84532], // Base Sepolia
          showQrModal: true,
          metadata: {
            name: 'Linguana',
            description: 'African Language Learning & Crowdsourcing Platform',
            url: 'https://linguana.app',
            icons: ['https://linguana.app/icon.png'],
          },
        });

        // Enable session (shows QR modal)
        console.log('[useWalletAuth] Enabling WalletConnect session...');
        const accounts = await provider.enable();
        walletAddress = accounts[0];
        console.log('[useWalletAuth] Connected wallet:', walletAddress);

        // Get nonce from backend
        const nonceResponse = await axios.post(`${API_URL}/api/auth/wallet/nonce/`, {
          wallet_address: walletAddress,
        });

        const { message } = nonceResponse.data;

        // Sign message
        signature = await provider.request({
          method: 'personal_sign',
          params: [message, walletAddress],
        }) as string;

      } else if (method === 'base' || method === 'coinbase') {
        console.log('[useWalletAuth] Initializing Coinbase Wallet SDK...');
        // Use Coinbase Wallet SDK directly for better control
        const coinbaseWallet = new CoinbaseWalletSDK({
          appName: 'Linguana',
          appLogoUrl: 'https://linguana.app/icon.png',
          appChainIds: [84532], // Base Sepolia
        });

        const provider = coinbaseWallet.makeWeb3Provider({
          options: method === 'base' ? 'smartWalletOnly' : 'all',
        });

        console.log('[useWalletAuth] Requesting accounts...');
        const accounts = await provider.request({
          method: 'eth_requestAccounts',
        }) as string[];

        if (!accounts || accounts.length === 0) {
          throw new Error('No accounts found');
        }

        walletAddress = accounts[0];
        console.log('[useWalletAuth] Connected wallet:', walletAddress);

        // Switch to Base Sepolia
        try {
          await provider.request({
            method: 'wallet_switchEthereumChain',
            params: [{ chainId: '0x14a34' }], // Base Sepolia
          });
        } catch (switchError: any) {
          if (switchError.code === 4902) {
            await provider.request({
              method: 'wallet_addEthereumChain',
              params: [{
                chainId: '0x14a34',
                chainName: 'Base Sepolia',
                nativeCurrency: {
                  name: 'ETH',
                  symbol: 'ETH',
                  decimals: 18,
                },
                rpcUrls: ['https://sepolia.base.org'],
                blockExplorerUrls: ['https://sepolia.basescan.org'],
              }],
            });
          }
        }

        // Get nonce from backend
        console.log('[useWalletAuth] Fetching nonce from backend...');
        const nonceResponse = await axios.post(`${API_URL}/api/auth/wallet/nonce/`, {
          wallet_address: walletAddress,
        });

        const { message } = nonceResponse.data;
        console.log('[useWalletAuth] Got nonce, requesting signature...');

        // Sign message with provider
        signature = await provider.request({
          method: 'personal_sign',
          params: [message, walletAddress],
        }) as string;
        console.log('[useWalletAuth] Signature received:', signature);

      } else {
        throw new Error('Invalid wallet method');
      }

      // Authenticate with backend
      console.log('[useWalletAuth] Authenticating with backend...');
      console.log('[useWalletAuth] Sending - address:', walletAddress, 'signature:', signature);
      const authResponse = await axios.post<WalletAuthResponse>(`${API_URL}/api/auth/wallet/auth/`, {
        address: walletAddress,
        signature,
      });

      console.log('[useWalletAuth] Authentication successful:', authResponse.data);

      // Store tokens
      localStorage.setItem('access_token', authResponse.data.tokens.access);
      localStorage.setItem('refresh_token', authResponse.data.tokens.refresh);

      console.log('[useWalletAuth] Tokens stored, needs_onboarding:', authResponse.data.needs_onboarding);
      return authResponse.data;

    } catch (err: any) {
      console.error('[useWalletAuth] Error:', err);
      console.error('[useWalletAuth] Error response:', err.response?.data);
      const errorMsg = err.response?.data?.error 
        || err.response?.data?.address?.[0]
        || err.response?.data?.signature?.[0]
        || err.message 
        || 'Failed to connect wallet';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  const completeOnboarding = useCallback(async (data: { nickname: string; role: 'contributor' | 'validator' }) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('Not authenticated');
      }

      const response = await axios.post(`${API_URL}/api/auth/onboard/`, data, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      return response.data;
    } catch (err: any) {
      const errorMsg = err.response?.data?.nickname?.[0] || err.response?.data?.error || err.message || 'Failed to complete onboarding';
      setError(errorMsg);
      throw new Error(errorMsg);
    } finally {
      setLoading(false);
    }
  }, []);

  const disconnectWallet = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }, []);

  return {
    loading,
    error,
    connectWallet,
    completeOnboarding,
    disconnectWallet,
  };
}
