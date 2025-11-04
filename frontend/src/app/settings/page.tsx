'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Wallet, DollarSign, History, Settings as SettingsIcon } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { WalletConnect } from '@/components/WalletConnect/WalletConnect';
import { Button } from '@/components/ui/button';

export default function SettingsPage() {
  const router = useRouter();
  const { user, isAuthenticated, logout } = useAuth();
  const [rewards, setRewards] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    const fetchData = async () => {
      try {
        const [rewardsData, summaryData] = await Promise.all([
          api.getRewards({ limit: 10 }),
          api.getRewardsSummary(),
        ]);
        setRewards(rewardsData.results || []);
        setSummary(summaryData);
      } catch (error) {
        console.error('Failed to fetch data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [isAuthenticated, router]);

  const handleLogout = async () => {
    await logout();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-muted">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-4xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold mb-2">Settings & Rewards</h1>
          <p className="text-lg text-muted">Manage your account and view earnings</p>
        </div>

        {/* Profile Card */}
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-primary text-white flex items-center justify-center text-2xl font-bold">
                {user?.username?.charAt(0).toUpperCase()}
              </div>
              <div>
                <h2 className="text-xl font-bold">{user?.username}</h2>
                <p className="text-muted">{user?.email}</p>
              </div>
            </div>
            <Button onClick={handleLogout} variant="outline">
              Logout
            </Button>
          </div>
        </div>

        {/* Wallet Section */}
        <div>
          <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
            <Wallet className="w-6 h-6" />
            Wallet & Rewards
          </h2>
          {!user?.wallet_address ? (
            <WalletConnect />
          ) : (
            <div className="card">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                <div>
                  <p className="text-sm text-muted mb-1">Total Earned</p>
                  <p className="text-3xl font-bold text-primary">
                    ${summary?.total_earnings?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted mb-1">Pending</p>
                  <p className="text-3xl font-bold text-accent">
                    ${summary?.pending_earnings?.toFixed(2) || '0.00'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted mb-1">Confirmed</p>
                  <p className="text-3xl font-bold text-success">
                    ${summary?.confirmed_earnings?.toFixed(2) || '0.00'}
                  </p>
                </div>
              </div>
              <div className="p-4 bg-bg rounded-lg">
                <p className="text-sm">
                  <span className="font-semibold">Wallet:</span>{' '}
                  <span className="font-mono">{user.wallet_address}</span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Rewards History */}
        <div>
          <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
            <History className="w-6 h-6" />
            Recent Rewards
          </h2>
          <div className="card">
            {rewards.length === 0 ? (
              <div className="text-center py-8 text-muted">
                <DollarSign className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No rewards yet</p>
                <p className="text-sm mt-1">Start recording or validating to earn USDC</p>
              </div>
            ) : (
              <div className="space-y-3">
                {rewards.map((reward) => (
                  <div
                    key={reward.id}
                    className="flex items-center justify-between p-4 bg-bg rounded-lg"
                  >
                    <div>
                      <p className="font-semibold">
                        {reward.reward_type === 'clip_upload' ? 'Recording' : 'Validation'}
                      </p>
                      <p className="text-sm text-muted">
                        {new Date(reward.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-primary">
                        ${reward.amount_usdc?.toFixed(2)}
                      </p>
                      <p className={`text-xs ${
                        reward.status === 'confirmed' ? 'text-success' : 'text-accent'
                      }`}>
                        {reward.status}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Preferences */}
        <div>
          <h2 className="font-bold text-xl mb-4 flex items-center gap-2">
            <SettingsIcon className="w-6 h-6" />
            Preferences
          </h2>
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Email Notifications</p>
                <p className="text-sm text-muted">Receive updates about rewards</p>
              </div>
              <input type="checkbox" className="toggle" defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-semibold">Auto-upload Recordings</p>
                <p className="text-sm text-muted">Upload when online</p>
              </div>
              <input type="checkbox" className="toggle" defaultChecked />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
