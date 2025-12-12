import { ScanStatus } from '../types'
import { clsx } from 'clsx'
import { Loader2, CheckCircle2, XCircle, Clock, Ban } from 'lucide-react'

interface StatusBadgeProps {
  status: ScanStatus
  showIcon?: boolean
}

const statusConfig: Record<ScanStatus, { 
  label: string
  color: string
  icon: React.ElementType 
}> = {
  pending: { 
    label: '대기 중', 
    color: 'text-gray-400 bg-gray-400/10 border-gray-400/30',
    icon: Clock
  },
  running: { 
    label: '스캔 중', 
    color: 'text-accent-cyan bg-accent-cyan/10 border-accent-cyan/30',
    icon: Loader2
  },
  completed: { 
    label: '완료', 
    color: 'text-severity-low bg-severity-low/10 border-severity-low/30',
    icon: CheckCircle2
  },
  failed: { 
    label: '실패', 
    color: 'text-severity-critical bg-severity-critical/10 border-severity-critical/30',
    icon: XCircle
  },
  cancelled: { 
    label: '취소됨', 
    color: 'text-severity-medium bg-severity-medium/10 border-severity-medium/30',
    icon: Ban
  },
}

export default function StatusBadge({ status, showIcon = true }: StatusBadgeProps) {
  const config = statusConfig[status]
  const Icon = config.icon
  
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-3 py-1 text-sm font-medium rounded-full border',
        config.color
      )}
    >
      {showIcon && (
        <Icon 
          className={clsx(
            'w-4 h-4',
            status === 'running' && 'animate-spin'
          )} 
        />
      )}
      {config.label}
    </span>
  )
}

