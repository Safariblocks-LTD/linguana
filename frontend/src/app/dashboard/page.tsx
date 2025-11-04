'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, CheckCircle, DollarSign, Flame, TrendingUp } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import { ProgressRing } from '@/components/ProgressRing/ProgressRing';
import { Badge } from '@/components/Badge/Badge';
import { WalletConnect } from '@/components/WalletConnect/WalletConnect';

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    const fetchStats = async () => {
      try {
        const [dashboardData, rewardsSummary] = await Promise.all([
          api.getDashboard(),
          api.getRewardsSummary(),
        ]);
        setStats({ ...dashboardData, ...rewardsSummary });
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [isAuthenticated, router]);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-primary border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-muted">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-12">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold mb-2">
            Welcome back, {user?.username}!
          </h1>
          <p className="text-lg text-muted">Here's your progress overview</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                <Mic className="w-5 h-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted">Recordings</p>
                <p className="text-2xl font-bold">{stats?.total_clips || 0}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                <CheckCircle className="w-5 h-5 text-success" />
              </div>
              <div>
                <p className="text-sm text-muted">Validations</p>
                <p className="text-2xl font-bold">{stats?.total_annotations || 0}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-accent" />
              </div>
              <div>
                <p className="text-sm text-muted">Total Earned</p>
                <p className="text-2xl font-bold">${stats?.total_earnings?.toFixed(2) || '0.00'}</p>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-lg bg-danger/10 flex items-center justify-center">
                <Flame className="w-5 h-5 text-danger" />
              </div>
              <div>
                <p className="text-sm text-muted">Streak</p>
                <p className="text-2xl font-bold">{stats?.streak_days || 0} days</p>
              </div>
            </div>
          </div>
        </div>

        {/* Progress Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h2 className="font-bold text-lg mb-6">Your Progress</h2>
            <div className="flex justify-around items-center">
              <div className="text-center">
                <ProgressRing
                  progress={Math.min((stats?.total_clips || 0) / 10 * 100, 100)}
                  label="Recordings"
                />
                <p className="mt-2 text-sm text-muted">
                  {stats?.total_clips || 0} / 10 clips
                </p>
              </div>
              <div className="text-center">
                <ProgressRing
                  progress={Math.min((stats?.total_annotations || 0) / 50 * 100, 100)}
                  color="#FF9F42"
                  label="Validations"
                />
                <p className="mt-2 text-sm text-muted">
                  {stats?.total_annotations || 0} / 50 validations
                </p>
              </div>
            </div>
          </div>

          <div className="card">
            <h2 className="font-bold text-lg mb-4">Quick Actions</h2>
            <div className="space-y-3">
              <button
                onClick={() => router.push('/record')}
                className="btn-primary w-full"
              >
                <Mic className="w-5 h-5 mr-2" />
                Record Audio
              </button>
              <button
                onClick={() => router.push('/tasks')}
                className="btn-secondary w-full"
              >
                <CheckCircle className="w-5 h-5 mr-2" />
                Validate Clips
              </button>
              <button
                onClick={() => router.push('/settings')}
                className="btn-secondary w-full"
              >
                <TrendingUp className="w-5 h-5 mr-2" />
                View Rewards
              </button>
            </div>
          </div>
        </div>

        {/* Wallet Section */}
        {!user?.wallet_address && (
          <WalletConnect />
        )}

        {/* Badges */}
        <div>
          <h2 className="font-bold text-2xl mb-6">Your Badges</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
            <Badge
              name="First Steps"
              description="Record your first clip"
              icon="star"
              earned={stats?.total_clips > 0}
              earnedAt={stats?.total_clips > 0 ? new Date() : undefined}
            />
            <Badge
              name="Validator"
              description="Complete 10 validations"
              icon="award"
              earned={stats?.total_annotations >= 10}
            />
            <Badge
              name="Contributor"
              description="Record 10 clips"
              icon="zap"
              earned={stats?.total_clips >= 10}
            />
            <Badge
              name="Champion"
              description="Earn $10 USDC"
              icon="trophy"
              earned={stats?.total_earnings >= 10}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
