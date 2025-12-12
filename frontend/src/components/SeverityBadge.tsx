import { Severity } from '../types'
import { clsx } from 'clsx'

interface SeverityBadgeProps {
  severity: Severity
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

const severityConfig: Record<Severity, { label: string; color: string }> = {
  critical: { label: 'Critical', color: 'severity-critical' },
  high: { label: 'High', color: 'severity-high' },
  medium: { label: 'Medium', color: 'severity-medium' },
  low: { label: 'Low', color: 'severity-low' },
  info: { label: 'Info', color: 'severity-info' },
}

const sizeConfig = {
  sm: 'px-2 py-0.5 text-xs',
  md: 'px-3 py-1 text-sm',
  lg: 'px-4 py-1.5 text-base',
}

export default function SeverityBadge({ 
  severity, 
  size = 'md',
  showLabel = true 
}: SeverityBadgeProps) {
  const config = severityConfig[severity]
  
  return (
    <span
      className={clsx(
        'inline-flex items-center font-semibold rounded-full border uppercase tracking-wide',
        config.color,
        sizeConfig[size]
      )}
    >
      {showLabel ? config.label : severity.charAt(0).toUpperCase()}
    </span>
  )
}

