'use client';

import { useState } from 'react';
import { Loader2, Shield } from 'lucide-react';
import Image from 'next/image';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface OptInModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onWalletConnect: (method: 'reown' | 'base' | 'coinbase') => Promise<void>;
}

export function OptInModal({ open, onOpenChange, onWalletConnect }: OptInModalProps) {
  const [connecting, setConnecting] = useState<'reown' | 'base' | 'coinbase' | null>(null);

  const handleConnect = async (method: 'reown' | 'base' | 'coinbase') => {
    setConnecting(method);
    try {
      await onWalletConnect(method);
    } catch (error) {
      console.error('Connection error:', error);
    } finally {
      setConnecting(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px] bg-gradient-to-br from-gray-900 to-black border-[#54e6b6]/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center bg-gradient-to-r from-[#54e6b6] to-white bg-clip-text text-transparent">
            Opt In — Connect your wallet
          </DialogTitle>
          <DialogDescription className="text-center text-gray-300 text-base mt-2">
            One click to contribute & earn USDC. Choose a wallet to continue.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-3 mt-4">
          {/* Base Smart Wallet */}
          <button
            onClick={() => handleConnect('base')}
            disabled={connecting !== null}
            className="w-full group relative overflow-hidden rounded-xl border-2 border-[#0052FF]/30 bg-gradient-to-br from-[#0052FF]/10 to-transparent hover:from-[#0052FF]/20 hover:border-[#0052FF]/50 transition-all p-6 text-left disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#0052FF]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <svg width="24" height="24" viewBox="0 0 111 111" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M54.921 110.034C85.359 110.034 110.034 85.402 110.034 55.017C110.034 24.6319 85.359 0 54.921 0C26.0432 0 2.35281 22.1714 0 50.3923H72.8467V59.6416H3.9565e-07C2.35281 87.8625 26.0432 110.034 54.921 110.034Z" fill="#0052FF"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white mb-1">Sign in with Base</h3>
                <p className="text-sm text-gray-400">
                  Create a smart wallet with passkey. No app needed.
                </p>
              </div>
              {connecting === 'base' && (
                <Loader2 className="w-5 h-5 text-[#0052FF] animate-spin" />
              )}
            </div>
          </button>

          {/* WalletConnect */}
          <button
            onClick={() => handleConnect('reown')}
            disabled={connecting !== null}
            className="w-full group relative overflow-hidden rounded-xl border-2 border-[#3B99FC]/30 bg-gradient-to-br from-[#3B99FC]/10 to-transparent hover:from-[#3B99FC]/20 hover:border-[#3B99FC]/50 transition-all p-6 text-left disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#3B99FC]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <svg width="24" height="24" viewBox="0 0 480 332" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M126.613 93.9842C197.814 23.2584 312.186 23.2584 383.387 93.9842L391.896 102.426C395.553 106.059 395.553 112.03 391.896 115.663L364.632 142.704C362.804 144.52 359.889 144.52 358.061 142.704L346.574 131.312C299.283 84.3068 220.717 84.3068 173.426 131.312L161.096 143.545C159.268 145.361 156.353 145.361 154.525 143.545L127.261 116.504C123.604 112.871 123.604 106.9 127.261 103.267L126.613 93.9842ZM437.877 151.94L461.999 175.914C465.656 179.547 465.656 185.518 461.999 189.151L337.547 312.299C333.89 315.932 327.906 315.932 324.249 312.299L239.226 227.83C238.312 226.922 236.688 226.922 235.774 227.83L150.751 312.299C147.094 315.932 141.11 315.932 137.453 312.299L13.001 189.151C9.344 185.518 9.344 179.547 13.001 175.914L37.123 151.94C40.78 148.307 46.764 148.307 50.421 151.94L135.444 236.409C136.358 237.317 137.982 237.317 138.896 236.409L223.919 151.94C227.576 148.307 233.56 148.307 237.217 151.94L322.24 236.409C323.154 237.317 324.778 237.317 325.692 236.409L410.715 151.94C414.372 148.307 420.356 148.307 424.013 151.94H437.877Z" fill="#3B99FC"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white mb-1">WalletConnect</h3>
                <p className="text-sm text-gray-400">
                  Connect 350+ wallets including MetaMask, Trust, Rainbow.
                </p>
              </div>
              {connecting === 'reown' && (
                <Loader2 className="w-5 h-5 text-[#3B99FC] animate-spin" />
              )}
            </div>
          </button>

          {/* Coinbase Wallet */}
          <button
            onClick={() => handleConnect('coinbase')}
            disabled={connecting !== null}
            className="w-full group relative overflow-hidden rounded-xl border-2 border-[#0052FF]/30 bg-gradient-to-br from-[#0052FF]/10 to-transparent hover:from-[#0052FF]/20 hover:border-[#0052FF]/50 transition-all p-6 text-left disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-xl bg-[#0052FF]/20 flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                <svg width="24" height="24" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <rect width="1024" height="1024" rx="512" fill="#0052FF"/>
                  <path fillRule="evenodd" clipRule="evenodd" d="M152 512C152 710.823 313.177 872 512 872C710.823 872 872 710.823 872 512C872 313.177 710.823 152 512 152C313.177 152 152 313.177 152 512ZM420 396C406.745 396 396 406.745 396 420V604C396 617.255 406.745 628 420 628H604C617.255 628 628 617.255 628 604V420C628 406.745 617.255 396 604 396H420Z" fill="white"/>
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-bold text-white mb-1">Coinbase Wallet</h3>
                <p className="text-sm text-gray-400">
                  Use Coinbase Wallet extension or mobile app.
                </p>
              </div>
              {connecting === 'coinbase' && (
                <Loader2 className="w-5 h-5 text-[#0052FF] animate-spin" />
              )}
            </div>
          </button>
        </div>

        <div className="mt-6 pt-4 border-t border-gray-800">
          <div className="flex items-center justify-center gap-2 text-xs text-gray-500">
            <Shield className="w-3 h-3" />
            <span>Secure wallet authentication on Base network</span>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
