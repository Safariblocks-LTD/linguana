'use client';

import { useState } from 'react';
import { User, CheckCircle2, Mic, Shield, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';

interface OnboardingModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onComplete: (data: { nickname: string; role: 'contributor' | 'validator' }) => Promise<void>;
  walletAddress?: string;
}

export function OnboardingModal({ open, onOpenChange, onComplete, walletAddress }: OnboardingModalProps) {
  const [nickname, setNickname] = useState('');
  const [role, setRole] = useState<'contributor' | 'validator' | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!nickname || !role) {
      setError('Please fill in all fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await onComplete({ nickname, role });
      onOpenChange(false);
    } catch (err: any) {
      setError(err.message || 'Failed to complete onboarding');
    } finally {
      setLoading(false);
    }
  };

  const formatAddress = (addr: string) => {
    return `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px] bg-gradient-to-br from-gray-900 to-black border-[#54e6b6]/20">
        <DialogHeader>
          <DialogTitle className="text-2xl font-bold text-center bg-gradient-to-r from-[#54e6b6] to-white bg-clip-text text-transparent">
            Welcome to Linguana!
          </DialogTitle>
          <DialogDescription className="text-center text-gray-300 text-base mt-2">
            Complete your profile to start contributing and earning USDC.
          </DialogDescription>
        </DialogHeader>

        {walletAddress && (
          <div className="flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-[#54e6b6]/10 border border-[#54e6b6]/30">
            <CheckCircle2 className="w-4 h-4 text-[#54e6b6]" />
            <span className="text-sm text-gray-300">
              Connected: <span className="font-mono text-[#54e6b6]">{formatAddress(walletAddress)}</span>
            </span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6 mt-4">
          {/* Nickname Input */}
          <div>
            <label htmlFor="nickname" className="block text-sm font-medium text-gray-300 mb-2">
              Choose your @nickname
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input
                id="nickname"
                type="text"
                value={nickname}
                onChange={(e) => {
                  setNickname(e.target.value);
                  setError(null);
                }}
                placeholder="username"
                className="w-full pl-10 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-[#54e6b6] focus:border-transparent"
                disabled={loading}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              This will be your public display name (3+ characters, alphanumeric)
            </p>
          </div>

          {/* Role Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              Select your role
            </label>
            <div className="space-y-3">
              {/* Contributor */}
              <button
                type="button"
                onClick={() => {
                  setRole('contributor');
                  setError(null);
                }}
                className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                  role === 'contributor'
                    ? 'border-[#54e6b6] bg-[#54e6b6]/10'
                    : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
                }`}
                disabled={loading}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    role === 'contributor' ? 'bg-[#54e6b6]/20' : 'bg-gray-700/50'
                  }`}>
                    <Mic className={`w-5 h-5 ${role === 'contributor' ? 'text-[#54e6b6]' : 'text-gray-400'}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-semibold mb-1 ${role === 'contributor' ? 'text-[#54e6b6]' : 'text-white'}`}>
                      Contributor
                    </h3>
                    <p className="text-sm text-gray-400">
                      Record and upload language data. Earn rewards for quality contributions.
                    </p>
                  </div>
                  {role === 'contributor' && (
                    <CheckCircle2 className="w-5 h-5 text-[#54e6b6] flex-shrink-0" />
                  )}
                </div>
              </button>

              {/* Validator */}
              <button
                type="button"
                onClick={() => {
                  setRole('validator');
                  setError(null);
                }}
                className={`w-full p-4 rounded-xl border-2 transition-all text-left ${
                  role === 'validator'
                    ? 'border-[#54e6b6] bg-[#54e6b6]/10'
                    : 'border-gray-700 bg-gray-800/30 hover:border-gray-600'
                }`}
                disabled={loading}
              >
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                    role === 'validator' ? 'bg-[#54e6b6]/20' : 'bg-gray-700/50'
                  }`}>
                    <Shield className={`w-5 h-5 ${role === 'validator' ? 'text-[#54e6b6]' : 'text-gray-400'}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-semibold mb-1 ${role === 'validator' ? 'text-[#54e6b6]' : 'text-white'}`}>
                      Validator
                    </h3>
                    <p className="text-sm text-gray-400">
                      Review and validate contributions. Help maintain data quality and earn rewards.
                    </p>
                  </div>
                  {role === 'validator' && (
                    <CheckCircle2 className="w-5 h-5 text-[#54e6b6] flex-shrink-0" />
                  )}
                </div>
              </button>
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
              {error}
            </div>
          )}

          <Button
            type="submit"
            disabled={!nickname || !role || loading}
            className="w-full bg-gradient-to-r from-[#54e6b6] to-[#40c4c4] hover:from-[#40c4c4] hover:to-[#54e6b6] text-black font-semibold py-6 text-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                Setting up your account...
              </>
            ) : (
              'Finish & Continue'
            )}
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
