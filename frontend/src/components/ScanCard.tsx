import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ExternalLink, Clock, AlertTriangle } from 'lucide-react'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import { Scan } from '../types'
import StatusBadge from './StatusBadge'

interface ScanCardProps {
  scan: Scan
  index?: number
}

export default function ScanCard({ scan, index = 0 }: ScanCardProps) {
  const hasVulnerabilities = scan.total_vulnerabilities > 0
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
    >
      <Link to={`/scan/${scan.id}`}>
        <div className="card card-hover group">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h3 className="text-lg font-semibold text-white truncate group-hover:text-primary-400 transition-colors">
                  {scan.target_domain}
                </h3>
                <StatusBadge status={scan.status} />
              </div>
              
              <p className="text-sm text-gray-400 truncate mb-4">
                {scan.target_url}
              </p>
              
              {/* Vulnerability summary */}
              {scan.status === 'completed' && (
                <div className="flex items-center gap-4 text-sm">
                  {hasVulnerabilities ? (
                    <>
                      {scan.critical_count > 0 && (
                        <span className="text-severity-critical">
                          {scan.critical_count} Critical
                        </span>
                      )}
                      {scan.high_count > 0 && (
                        <span className="text-severity-high">
                          {scan.high_count} High
                        </span>
                      )}
                      {scan.medium_count > 0 && (
                        <span className="text-severity-medium">
                          {scan.medium_count} Medium
                        </span>
                      )}
                      {scan.low_count > 0 && (
                        <span className="text-severity-low">
                          {scan.low_count} Low
                        </span>
                      )}
                    </>
                  ) : (
                    <span className="text-severity-low flex items-center gap-1">
                      <AlertTriangle className="w-4 h-4" />
                      취약점이 발견되지 않았습니다
                    </span>
                  )}
                </div>
              )}
              
              {/* Progress bar for running scans */}
              {scan.status === 'running' && (
                <div className="mt-3">
                  <div className="flex items-center justify-between text-sm mb-1">
                    <span className="text-gray-400">진행률</span>
                    <span className="text-primary-400">{scan.progress}%</span>
                  </div>
                  <div className="h-2 bg-dark-700 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-primary-500 to-accent-cyan"
                      initial={{ width: 0 }}
                      animate={{ width: `${scan.progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              )}
            </div>
            
            <ExternalLink className="w-5 h-5 text-gray-500 group-hover:text-primary-400 transition-colors flex-shrink-0" />
          </div>
          
          {/* Footer */}
          <div className="flex items-center gap-4 mt-4 pt-4 border-t border-white/5 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Clock className="w-4 h-4" />
              {format(new Date(scan.created_at), 'PPP p', { locale: ko })}
            </span>
            <span className="capitalize">{scan.scan_type} 스캔</span>
          </div>
        </div>
      </Link>
    </motion.div>
  )
}

