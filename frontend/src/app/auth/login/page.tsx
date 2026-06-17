'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Eye, EyeOff, Lock, Mail } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(1, 'Password is required'),
})
type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const [showPw, setShowPw] = useState(false)
  const { login, isLoading } = useAuthStore()
  const router = useRouter()

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await login(data)
      toast.success('Welcome back!')
      router.push('/dashboard')
    } catch (e: any) {
      toast.error(e?.message || 'Login failed')
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_60%_50%,rgba(3,100,209,0.1),transparent_70%)] pointer-events-none" />

      <div className="relative w-full max-w-sm">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-2 mb-3">
            <svg width="36" height="36" viewBox="0 0 48 48" fill="none">
              <path d="M4 36V12L14 28V12" stroke="#0364D1" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M18 36V12L28 28V12" stroke="#0364D1" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M30 28L38 12L46 28" stroke="#00C48C" strokeWidth="3" strokeLinecap="round"/>
              <path d="M33 18L38 9L43 18" stroke="#00C48C" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <div>
              <div className="font-bold text-lg leading-none">DOUBLE N</div>
              <div className="text-xs text-slate tracking-widest">TRADING</div>
            </div>
          </div>
          <p className="text-slate text-sm">Sign in to your account</p>
        </div>

        <div className="card p-7">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email */}
            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
                <input
                  {...register('email')}
                  type="email"
                  autoFocus
                  autoComplete="email"
                  placeholder="you@example.com"
                  className={cn('input-field pl-9', errors.email && 'border-danger focus:ring-danger')}
                />
              </div>
              {errors.email && <p className="text-danger text-xs mt-1">{errors.email.message}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
                <input
                  {...register('password')}
                  type={showPw ? 'text' : 'password'}
                  autoComplete="current-password"
                  placeholder="••••••••"
                  className={cn('input-field pl-9 pr-10', errors.password && 'border-danger focus:ring-danger')}
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate hover:text-white transition-colors">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-danger text-xs mt-1">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full py-3 mt-2">
              {isLoading
                ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : 'Sign In'
              }
            </button>
          </form>

          <p className="text-center text-sm text-slate mt-5">
            Don&apos;t have an account?{' '}
            <Link href="/auth/register" className="text-blue hover:text-blue-light font-medium transition-colors">
              Create one
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
