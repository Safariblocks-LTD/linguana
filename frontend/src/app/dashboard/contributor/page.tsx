'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Mic, DollarSign, Flame, TrendingUp, Upload, Award, LogOut, User as UserIcon, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';

export default function ContributorDashboard() {
  const router = useRouter();
  const [user, setUser] = useState<any>(null);
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [copied, setCopied] = useState(false);

  const handleCopyAddress = () => {
    if (user?.wallet_address) {
      navigator.clipboard.writeText(user.wallet_address);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    router.push('/');
  };

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/');
      return;
    }

    // Fetch user data and stats
    const fetchData = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/profile/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          console.log('[Dashboard] User data:', userData);
          setUser(userData);
          
          // Fetch stats
          const statsResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/stats/`, {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          });
          
          if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            setStats(statsData);
          }
        } else {
          router.push('/');
        }
      } catch (error) {
        console.error('[Dashboard] Failed to fetch data:', error);
        router.push('/');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin w-12 h-12 border-4 border-[#54e6b6] border-t-transparent rounded-full mx-auto" />
          <p className="mt-4 text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-black">
      {/* Header */}
      <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-[#54e6b6] to-[#40c4c4] rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-xl">L</span>
              </div>
              <span className="text-xl font-bold text-white">Linguana</span>
            </div>
            <div className="flex items-center space-x-4">
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 hover:border-[#54e6b6]/50 transition-colors cursor-pointer">
                    <div className="w-8 h-8 rounded-full bg-[#54e6b6]/20 flex items-center justify-center">
                      <span className="text-[#54e6b6] font-semibold text-sm">
                        {user?.nickname?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div className="text-left">
                      <p className="text-sm font-semibold text-white">@{user?.nickname || 'user'}</p>
                      <p className="text-xs text-gray-400 font-mono">
                        {user?.wallet_address ? `${user.wallet_address.substring(0, 6)}...${user.wallet_address.substring(38)}` : ''}
                      </p>
                    </div>
                  </button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64">
                  <div className="px-2 py-2">
                    <p className="text-sm font-semibold text-white">@{user?.nickname || 'user'}</p>
                    <p className="text-xs text-gray-400">{user?.role || 'contributor'}</p>
                  </div>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleCopyAddress} className="cursor-pointer">
                    {copied ? <Check className="w-4 h-4 mr-2" /> : <Copy className="w-4 h-4 mr-2" />}
                    <span className="flex-1">{copied ? 'Copied!' : 'Copy wallet address'}</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer font-mono text-xs text-gray-400">
                    <UserIcon className="w-4 h-4 mr-2" />
                    {user?.wallet_address ? `${user.wallet_address.substring(0, 10)}...${user.wallet_address.substring(32)}` : ''}
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-red-400 hover:text-red-300 hover:bg-red-500/10">
                    <LogOut className="w-4 h-4 mr-2" />
                    Disconnect wallet
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="space-y-8">
          {/* Welcome Section */}
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">
              Welcome back, @{user?.nickname}!
            </h1>
            <p className="text-lg text-gray-400">Ready to contribute and earn USDC?</p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#54e6b6]/20 flex items-center justify-center">
                    <Mic className="w-5 h-5 text-[#54e6b6]" />
                  </div>
                  <div>
                    <CardDescription className="text-gray-400">Contributions</CardDescription>
                    <CardTitle className="text-2xl text-white">{stats?.total_clips_uploaded || 0}</CardTitle>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-green-400" />
                  </div>
                  <div>
                    <CardDescription className="text-gray-400">Total Earned</CardDescription>
                    <CardTitle className="text-2xl text-white">${stats?.total_earned || '0.00'}</CardTitle>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                    <Flame className="w-5 h-5 text-orange-400" />
                  </div>
                  <div>
                    <CardDescription className="text-gray-400">Streak</CardDescription>
                    <CardTitle className="text-2xl text-white">{stats?.current_streak || 0} days</CardTitle>
                  </div>
                </div>
              </CardHeader>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader className="pb-3">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-500/20 flex items-center justify-center">
                    <Award className="w-5 h-5 text-purple-400" />
                  </div>
                  <div>
                    <CardDescription className="text-gray-400">Level</CardDescription>
                    <CardTitle className="text-2xl text-white">{stats?.level || 1}</CardTitle>
                  </div>
                </div>
              </CardHeader>
            </Card>
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gradient-to-br from-[#54e6b6]/10 to-transparent border-[#54e6b6]/30">
              <CardHeader>
                <CardTitle className="text-white">Quick Actions</CardTitle>
                <CardDescription className="text-gray-400">Start contributing now</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button
                  onClick={() => router.push('/record')}
                  className="w-full bg-gradient-to-r from-[#54e6b6] to-[#40c4c4] hover:from-[#40c4c4] hover:to-[#54e6b6] text-black font-semibold"
                  size="lg"
                >
                  <Mic className="w-5 h-5 mr-2" />
                  Record Audio Clip
                </Button>
                <Button
                  onClick={() => router.push('/record')}
                  variant="outline"
                  className="w-full border-gray-700 text-white hover:bg-gray-800"
                  size="lg"
                >
                  <Upload className="w-5 h-5 mr-2" />
                  Upload Existing Audio
                </Button>
              </CardContent>
            </Card>

            <Card className="bg-gray-800/50 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Earnings Overview</CardTitle>
                <CardDescription className="text-gray-400">Your USDC balance</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Available Balance</span>
                    <span className="text-2xl font-bold text-[#54e6b6]">${stats?.balance_usdc || '0.00'}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Total Earned</span>
                    <span className="text-white">${stats?.total_earned || '0.00'}</span>
                  </div>
                  <Button
                    variant="outline"
                    className="w-full border-[#54e6b6] text-[#54e6b6] hover:bg-[#54e6b6]/10"
                  >
                    <TrendingUp className="w-4 h-4 mr-2" />
                    View Earnings History
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card className="bg-gray-800/50 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">Recent Contributions</CardTitle>
              <CardDescription className="text-gray-400">Your latest audio uploads</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-gray-500">
                <Mic className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>No contributions yet. Start recording to see your activity here!</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
