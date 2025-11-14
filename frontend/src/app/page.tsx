'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Mic, CheckCircle2, DollarSign, Activity } from 'lucide-react'
import { ThemeToggle } from '@/components/ThemeToggle/ThemeToggle'
import { OptInModal } from '@/components/OptInModal/OptInModal'
import { OnboardingModal } from '@/components/OnboardingModal/OnboardingModal'
import { useWalletAuth } from '@/hooks/useWalletAuth'

export default function Home() {
  const router = useRouter()
  const { connectWallet, completeOnboarding, loading, error } = useWalletAuth()
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [asrStatus, setAsrStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [optInModalOpen, setOptInModalOpen] = useState(false)
  const [onboardingModalOpen, setOnboardingModalOpen] = useState(false)
  const [walletAddress, setWalletAddress] = useState<string | undefined>()
  const [authError, setAuthError] = useState<string | null>(null)

  useEffect(() => {
    // Check backend API
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/`)
      .then(res => res.json())
      .then(() => setApiStatus('online'))
      .catch(() => setApiStatus('offline'))

    // Check ASR service
    fetch(`${process.env.NEXT_PUBLIC_ASR_URL}/health`)
      .then(res => res.json())
      .then(() => setAsrStatus('online'))
      .catch(() => setAsrStatus('offline'))
  }, [])

  const handleWalletConnect = async (method: 'reown' | 'base' | 'coinbase') => {
    console.log('[HomePage] handleWalletConnect called with method:', method);
    try {
      setAuthError(null)
      console.log('[HomePage] Calling connectWallet...');
      const response = await connectWallet(method)
      console.log('[HomePage] connectWallet response:', response);
      setWalletAddress(response.user.wallet_address)
      
      if (response.needs_onboarding) {
        console.log('[HomePage] User needs onboarding, opening onboarding modal');
        setOptInModalOpen(false)
        setOnboardingModalOpen(true)
      } else {
        console.log('[HomePage] User already onboarded, redirecting to dashboard');
        // Redirect to dashboard based on role
        const dashboardPath = response.user.role === 'validator' ? '/dashboard/validator' : '/dashboard/contributor'
        router.push(dashboardPath)
      }
    } catch (err: any) {
      console.error('[HomePage] Error in handleWalletConnect:', err);
      setAuthError(err.message)
    }
  }

  const handleOnboardingComplete = async (data: { nickname: string; role: 'contributor' | 'validator' }) => {
    try {
      setAuthError(null)
      await completeOnboarding(data)
      
      // Redirect to dashboard based on role
      const dashboardPath = data.role === 'validator' ? '/dashboard/validator' : '/dashboard/contributor'
      router.push(dashboardPath)
    } catch (err: any) {
      setAuthError(err.message)
      throw err
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black transition-colors">
      {/* Header */}
      <nav className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg shadow-soft sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-primary to-primary-600 rounded-lg flex items-center justify-center shadow-lg">
                <span className="text-white font-bold text-xl">L</span>
              </div>
              <span className="text-xl font-bold text-gray-900 dark:text-white">Linguana</span>
            </div>
            <div className="flex items-center space-x-4">
              <ThemeToggle />
              <Button 
                onClick={() => setOptInModalOpen(true)}
                className="bg-gradient-to-r from-[#54e6b6] to-[#40c4c4] hover:from-[#40c4c4] hover:to-[#54e6b6] text-black font-semibold shadow-lg hover:shadow-xl transition-all"
              >
                Opt In
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          {/* Animated badge */}
          <div className="inline-flex items-center px-4 py-2 rounded-full bg-primary/10 dark:bg-primary/20 border border-primary/20 mb-6 animate-pulse">
            <Activity className="w-4 h-4 text-primary mr-2" />
            <span className="text-sm font-semibold text-primary">Preserving African Languages</span>
          </div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 text-gray-900 dark:text-white leading-tight">
            Learn African Languages
            <br />
            & Dialects.{' '}
            <span className="bg-gradient-to-r from-primary via-primary-600 to-accent bg-clip-text text-transparent">
              Earn Rewards
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
            Contribute audio clips in African languages and dialects. Validate transcriptions. 
            Earn rewards while preserving African languages.
          </p>
          
          {/* Status Indicators */}
          <div className="flex justify-center space-x-6 mb-12">
            <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <div className={`w-3 h-3 rounded-full ${apiStatus === 'online' ? 'bg-green-500' : apiStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`}></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">Backend API</span>
            </div>
            <div className="flex items-center space-x-2 px-4 py-2 rounded-full bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
              <div className={`w-3 h-3 rounded-full ${asrStatus === 'online' ? 'bg-green-500' : asrStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`}></div>
              <span className="text-sm text-gray-600 dark:text-gray-400">ASR Service</span>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Button 
              size="lg" 
              onClick={() => setOptInModalOpen(true)}
              className="bg-gradient-to-r from-[#54e6b6] to-[#40c4c4] hover:from-[#40c4c4] hover:to-[#54e6b6] text-black font-semibold shadow-lg hover:shadow-xl transition-all px-8 py-6 text-lg"
            >
              Get Started Free
            </Button>
            <Button size="lg" variant="outline" className="border-2 border-gray-300 dark:border-gray-700 hover:border-[#54e6b6] dark:hover:border-[#54e6b6] text-gray-900 dark:text-white px-8 py-6 text-lg" asChild>
              <Link href="/dashboard">View Dashboard</Link>
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-2 border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-all hover:shadow-xl group">
            <CardHeader>
              <div className="w-14 h-14 bg-gradient-to-br from-primary/20 to-primary/10 dark:from-primary/30 dark:to-primary/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Mic className="w-7 h-7 text-primary" />
              </div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white mb-2">Record Audio</CardTitle>
              <CardDescription className="text-gray-600 dark:text-gray-400 leading-relaxed">
                Contribute audio clips in African languages and dialects and get instant pronunciation feedback.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-2 border-gray-200 dark:border-gray-700 hover:border-success dark:hover:border-success transition-all hover:shadow-xl group">
            <CardHeader>
              <div className="w-14 h-14 bg-gradient-to-br from-success/20 to-success/10 dark:from-success/30 dark:to-success/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <CheckCircle2 className="w-7 h-7 text-success" />
              </div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white mb-2">Validate Clips</CardTitle>
              <CardDescription className="text-gray-600 dark:text-gray-400 leading-relaxed">
                Help validate transcriptions and earn rewards through our consensus system.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-2 border-gray-200 dark:border-gray-700 hover:border-accent dark:hover:border-accent transition-all hover:shadow-xl group">
            <CardHeader>
              <div className="w-14 h-14 bg-gradient-to-br from-accent/20 to-accent/10 dark:from-accent/30 dark:to-accent/20 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <DollarSign className="w-7 h-7 text-accent" />
              </div>
              <CardTitle className="text-xl font-bold text-gray-900 dark:text-white mb-2">Earn Rewards</CardTitle>
              <CardDescription className="text-gray-600 dark:text-gray-400 leading-relaxed">
                Get paid in US Dollars for quality contributions and validations, transparently on the blockchain.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20">
          <div className="text-center p-6 rounded-2xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-all">
            <div className="text-5xl font-bold bg-gradient-to-r from-primary to-primary-600 bg-clip-text text-transparent">3</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2 font-medium">Dialects</div>
          </div>
          <div className="text-center p-6 rounded-2xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border border-gray-200 dark:border-gray-700 hover:border-accent dark:hover:border-accent transition-all">
            <div className="text-5xl font-bold bg-gradient-to-r from-accent to-yellow-500 bg-clip-text text-transparent">$0.20</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2 font-medium">Per Validated Clip</div>
          </div>
          <div className="text-center p-6 rounded-2xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border border-gray-200 dark:border-gray-700 hover:border-success dark:hover:border-success transition-all">
            <div className="text-5xl font-bold bg-gradient-to-r from-success to-green-600 bg-clip-text text-transparent">9</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2 font-medium">Badges to Earn</div>
          </div>
          <div className="text-center p-6 rounded-2xl bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm border border-gray-200 dark:border-gray-700 hover:border-primary dark:hover:border-primary transition-all">
            <div className="text-5xl font-bold bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">85%</div>
            <div className="text-gray-600 dark:text-gray-400 mt-2 font-medium">Consensus Threshold</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-700 mt-20 bg-white dark:bg-gray-900">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600 dark:text-gray-400">
            <p>© 2025 Linguana. Preserving African languages through technology.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      <OptInModal 
        open={optInModalOpen} 
        onOpenChange={setOptInModalOpen}
        onWalletConnect={handleWalletConnect}
      />
      <OnboardingModal 
        open={onboardingModalOpen} 
        onOpenChange={setOnboardingModalOpen}
        onComplete={handleOnboardingComplete}
        walletAddress={walletAddress}
      />
    </main>
  )
}
