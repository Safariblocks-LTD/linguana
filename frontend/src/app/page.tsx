'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Mic, CheckCircle2, DollarSign, Activity } from 'lucide-react'

export default function Home() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [asrStatus, setAsrStatus] = useState<'checking' | 'online' | 'offline'>('checking')

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

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white">
      {/* Header */}
      <nav className="border-b border-gray-700 bg-black/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-[#40C4C4] rounded-lg flex items-center justify-center">
                <span className="text-black font-bold text-xl">L</span>
              </div>
              <span className="text-xl font-bold">Linguana</span>
            </div>
            <div className="flex space-x-4">
              <Button variant="ghost" asChild>
                <Link href="/auth/login">Login</Link>
              </Button>
              <Button asChild>
                <Link href="/auth/register">Sign Up</Link>
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold mb-6">
            Learn Kenyan Dialects,
            <br />
            <span className="text-[#40C4C4]">Earn Crypto Rewards</span>
          </h1>
          <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
            Contribute audio clips in Sheng, Kiamu, and Kibajuni. Validate transcriptions. 
            Earn USDC on Base L2 while preserving African languages.
          </p>
          
          {/* Status Indicators */}
          <div className="flex justify-center space-x-6 mb-12">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${apiStatus === 'online' ? 'bg-green-500' : apiStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`}></div>
              <span className="text-sm text-gray-400">Backend API</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${asrStatus === 'online' ? 'bg-green-500' : asrStatus === 'offline' ? 'bg-red-500' : 'bg-yellow-500 animate-pulse'}`}></div>
              <span className="text-sm text-gray-400">ASR Service</span>
            </div>
          </div>

          <div className="flex justify-center space-x-4">
            <Button size="lg" asChild>
              <Link href="/auth/register">Get Started</Link>
            </Button>
            <Button size="lg" variant="outline" asChild>
              <Link href="/api-test">Test API</Link>
            </Button>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-20">
          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-[#40C4C4]/20 rounded-lg flex items-center justify-center mb-4">
                <Mic className="w-6 h-6 text-[#40C4C4]" />
              </div>
              <CardTitle>Record Audio</CardTitle>
              <CardDescription>
                Contribute audio clips in Kenyan dialects and get instant pronunciation feedback.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-[#40C4C4]/20 rounded-lg flex items-center justify-center mb-4">
                <CheckCircle2 className="w-6 h-6 text-[#40C4C4]" />
              </div>
              <CardTitle>Validate Clips</CardTitle>
              <CardDescription>
                Help validate transcriptions and earn rewards through our consensus system.
              </CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <div className="w-12 h-12 bg-[#40C4C4]/20 rounded-lg flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-[#40C4C4]" />
              </div>
              <CardTitle>Earn USDC</CardTitle>
              <CardDescription>
                Get paid in USDC on Base L2 for quality contributions and validations.
              </CardDescription>
            </CardHeader>
          </Card>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-4 gap-6 mt-20">
          <div className="text-center">
            <div className="text-4xl font-bold text-[#40C4C4]">3</div>
            <div className="text-gray-400 mt-2">Dialects</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-[#40C4C4]">$0.20</div>
            <div className="text-gray-400 mt-2">Per Validated Clip</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-[#40C4C4]">9</div>
            <div className="text-gray-400 mt-2">Badges to Earn</div>
          </div>
          <div className="text-center">
            <div className="text-4xl font-bold text-[#40C4C4]">85%</div>
            <div className="text-gray-400 mt-2">Consensus Threshold</div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-700 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-400">
            <p>© 2025 Linguana. Preserving African languages through technology.</p>
          </div>
        </div>
      </footer>
    </main>
  )
}
