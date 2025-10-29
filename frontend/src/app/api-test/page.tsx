'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Loader2 } from 'lucide-react'

export default function APITest() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const testBackendAPI = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/`)
      const data = await response.json()
      setResults({ backend: data })
    } catch (err: any) {
      setError(`Backend API Error: ${err.message}`)
    }
    setLoading(false)
  }

  const testASRService = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_ASR_URL}/health`)
      const data = await response.json()
      setResults({ asr: data })
    } catch (err: any) {
      setError(`ASR Service Error: ${err.message}`)
    }
    setLoading(false)
  }

  const testRegistration = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/register/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: `testuser_${Date.now()}`,
          email: `test_${Date.now()}@example.com`,
          password: 'Test123!',
          password_confirm: 'Test123!'
        })
      })
      const data = await response.json()
      setResults({ registration: data })
    } catch (err: any) {
      setError(`Registration Error: ${err.message}`)
    }
    setLoading(false)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold">API Connection Test</h1>
          <Button variant="outline" asChild>
            <Link href="/">← Back</Link>
          </Button>
        </div>

        <div className="space-y-4 mb-8">
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-400 mb-2">Backend API URL:</p>
              <p className="font-mono text-[#40C4C4]">{process.env.NEXT_PUBLIC_API_URL}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-6">
              <p className="text-sm text-gray-400 mb-2">ASR Service URL:</p>
              <p className="font-mono text-[#40C4C4]">{process.env.NEXT_PUBLIC_ASR_URL}</p>
            </CardContent>
          </Card>
        </div>

        <div className="grid md:grid-cols-3 gap-4 mb-8">
          <Button onClick={testBackendAPI} disabled={loading} size="lg" className="w-full">
            Test Backend API
          </Button>
          <Button onClick={testASRService} disabled={loading} size="lg" className="w-full">
            Test ASR Service
          </Button>
          <Button onClick={testRegistration} disabled={loading} size="lg" className="w-full">
            Test Registration
          </Button>
        </div>

        {loading && (
          <div className="text-center py-8">
            <Loader2 className="w-8 h-8 animate-spin mx-auto text-[#40C4C4]" />
            <p className="mt-4 text-gray-400">Testing connection...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-8">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {results && (
          <Card>
            <CardHeader>
              <CardTitle className="text-[#40C4C4]">Response:</CardTitle>
            </CardHeader>
            <CardContent>
              <pre className="bg-black/50 p-4 rounded-lg overflow-auto text-sm">
                {JSON.stringify(results, null, 2)}
              </pre>
            </CardContent>
          </Card>
        )}
      </div>
    </main>
  )
}
