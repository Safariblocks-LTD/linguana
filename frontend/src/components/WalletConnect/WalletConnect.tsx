'use client';

import { Wallet, CheckCircle, AlertCircle } from 'lucide-react';
import { useWallet } from '@/hooks/useWallet';
import { Button } from '@/components/ui/button';

export function WalletConnect() {
  const { address, isConnected, loading, error, connectWallet, disconnectWallet } = useWallet();

  const formatAddress = (addr: string) => {
    return `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;
  };

  if (isConnected && address) {
    return (
      <div className="card">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <CheckCircle className="w-6 h-6 text-success" />
            <div>
              <p className="font-semibold">Wallet Connected</p>
              <p className="text-sm text-muted font-mono">{formatAddress(address)}</p>
            </div>
          </div>
          <Button
            onClick={disconnectWallet}
            variant="outline"
            size="sm"
          >
            Disconnect
          </Button>
        </div>
        <div className="mt-4 p-3 bg-bg rounded-lg">
          <p className="text-sm text-muted">
            ⚡ Gas fees sponsored on Base Sepolia testnet
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="text-center space-y-4">
        <Wallet className="w-16 h-16 text-primary mx-auto" />
        <div>
          <h3 className="text-xl font-bold mb-2">Connect Your Wallet</h3>
          <p className="text-muted mb-4">
            Connect your Coinbase Wallet or MetaMask to receive USDC rewards on Base L2
          </p>
        </div>

        {error && (
          <div className="flex items-start gap-2 p-3 bg-danger/10 border border-danger rounded-lg text-sm">
            <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
            <p className="text-danger">{error}</p>
          </div>
        )}

        <Button
          onClick={connectWallet}
          disabled={loading}
          className="btn-primary w-full"
          size="lg"
        >
          <Wallet className="w-5 h-5 mr-2" />
          {loading ? 'Connecting...' : 'Connect Wallet'}
        </Button>

        <div className="text-xs text-muted space-y-1">
          <p>✓ Secure wallet authentication</p>
          <p>✓ Gas fees sponsored on testnet</p>
          <p>✓ Instant USDC rewards on Base</p>
        </div>
      </div>
    </div>
  );
}
