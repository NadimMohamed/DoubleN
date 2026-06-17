'use client'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { toast } from 'sonner'
import { Eye, EyeOff, Lock, Mail, User } from 'lucide-react'
import { useState } from 'react'
import { useAuthStore } from '@/store/authStore'
import { cn } from '@/lib/utils'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  username: z
    .string()
    .min(3, 'At least 3 characters')
    .max(30, 'Max 30 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Letters, numbers and underscores only'),
  password: z
    .string()
    .min(8, 'At least 8 characters')
    .regex(/[A-Z]/, 'Must contain an uppercase letter')
    .regex(/[0-9]/, 'Must contain a number'),
  full_name: z.string().optional(),
})
type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const [showPw, setShowPw] = useState(false)
  const { register: registerUser, isLoading } = useAuthStore()
  const router = useRouter()

  const { register, handleSubmit, formState: { errors } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await registerUser(data)
      toast.success('Account created! Welcome to Double N Trading.')
      router.push('/dashboard')
    } catch (e: any) {
      toast.error(e?.message || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen bg-navy flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_60%_50%,rgba(3,100,209,0.1),transparent_70%)] pointer-events-none" />

      <div className="relative w-full max-w-sm">
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
          <p className="text-slate text-sm">Create your trading account</p>
        </div>

        <div className="card p-7">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Full name (optional)</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
                <input {...register('full_name')} type="text" placeholder="John Doe"
                  className="input-field pl-9" autoFocus />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Email address</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
                <input {...register('email')} type="email" placeholder="you@example.com"
                  className={cn('input-field pl-9', errors.email && 'border-danger')} />
              </div>
              {errors.email && <p className="text-danger text-xs mt-1">{errors.email.message}</p>}
            </div>

            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Username</label>
              <div className="relative">
                <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate text-sm">@</span>
                <input {...register('username')} type="text" placeholder="trader123"
                  className={cn('input-field pl-7', errors.username && 'border-danger')} />
              </div>
              {errors.username && <p className="text-danger text-xs mt-1">{errors.username.message}</p>}
            </div>

            <div>
              <label className="block text-xs font-medium text-slate mb-1.5">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate" />
                <input {...register('password')} type={showPw ? 'text' : 'password'}
                  placeholder="Min 8 chars, uppercase, number"
                  className={cn('input-field pl-9 pr-10', errors.password && 'border-danger')} />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate hover:text-white">
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {errors.password && <p className="text-danger text-xs mt-1">{errors.password.message}</p>}
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full py-3 mt-2">
              {isLoading
                ? <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                : 'Create Account'
              }
            </button>
          </form>

          <p className="text-center text-sm text-slate mt-5">
            Already have an account?{' '}
            <Link href="/auth/login" className="text-blue hover:text-blue-light font-medium transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
