import { cn } from '@/lib/utils'

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
  label?: string
}

const sizes = { sm: 'w-4 h-4', md: 'w-6 h-6', lg: 'w-8 h-8' }

export function LoadingSpinner({ size = 'md', className, label }: LoadingSpinnerProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-2', className)}>
      <div className={cn('border-2 border-blue/30 border-t-blue rounded-full animate-spin', sizes[size])} />
      {label && <p className="text-sm text-slate">{label}</p>}
    </div>
  )
}

export function FullPageSpinner({ label = 'Loading…' }: { label?: string }) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-navy">
      <LoadingSpinner size="lg" label={label} />
    </div>
  )
}
