import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { 
  ArrowLeft, 
  Download,
  RefreshCw,
  ExternalLink,
  Clock,
  AlertTriangle,
  Shield,
  ChevronDown,
  ChevronUp,
  FileText
} from 'lucide-react'
import { format } from 'date-fns'
import { ko } from 'date-fns/locale'
import { useState } from 'react'
import toast from 'react-hot-toast'
import { scanAPI, vulnerabilityAPI, reportAPI } from '../services/api'
import StatusBadge from '../components/StatusBadge'
import SeverityBadge from '../components/SeverityBadge'
import { Vulnerability } from '../types'

export default function ScanDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [expandedVuln, setExpandedVuln] = useState<number | null>(null)
  
  const scanId = parseInt(id || '0')
  
  const { data: scan, isLoading: scanLoading, refetch } = useQuery({
    queryKey: ['scan', scanId],
    queryFn: () => scanAPI.get(scanId),
    refetchInterval: (data) => {
      if (data?.status === 'running' || data?.status === 'pending') {
        return 3000
      }
      return false
    },
  })
  
  const { data: vulnData, isLoading: vulnLoading } = useQuery({
    queryKey: ['vulnerabilities', scanId],
    queryFn: () => vulnerabilityAPI.getByScan(scanId),
    enabled: scan?.status === 'completed',
  })
  
  const vulnerabilities: Vulnerability[] = vulnData?.vulnerabilities || []
  
  const handleDownloadPDF = async () => {
    try {
      const blob = await reportAPI.downloadPDF(scanId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `securescan_report_${scanId}.pdf`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('PDF 보고서 다운로드 완료')
    } catch {
      toast.error('보고서 다운로드에 실패했습니다')
    }
  }
  
  const handleDownloadHTML = async () => {
    try {
      const blob = await reportAPI.downloadHTML(scanId)
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `securescan_report_${scanId}.html`
      a.click()
      window.URL.revokeObjectURL(url)
      toast.success('HTML 보고서 다운로드 완료')
    } catch {
      toast.error('보고서 다운로드에 실패했습니다')
    }
  }
  
  if (scanLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    )
  }
  
  if (!scan) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="w-12 h-12 text-gray-600 mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-white mb-2">스캔을 찾을 수 없습니다</h2>
        <button onClick={() => navigate('/dashboard')} className="btn btn-secondary mt-4">
          <ArrowLeft className="w-5 h-5" />
          대시보드로 돌아가기
        </button>
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate(-1)}
            className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-3">
              {scan.target_domain}
              <StatusBadge status={scan.status} />
            </h1>
            <p className="text-gray-400 text-sm mt-1 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              {format(new Date(scan.created_at), 'PPP p', { locale: ko })}
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          {scan.status === 'completed' && (
            <>
              <button onClick={handleDownloadPDF} className="btn btn-secondary">
                <Download className="w-4 h-4" />
                PDF
              </button>
              <button onClick={handleDownloadHTML} className="btn btn-secondary">
                <FileText className="w-4 h-4" />
                HTML
              </button>
            </>
          )}
          <button onClick={() => refetch()} className="btn btn-ghost">
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>
      
      {/* Progress Bar (for running scans) */}
      {(scan.status === 'running' || scan.status === 'pending') && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">스캔 진행 중</h2>
            <span className="text-primary-400 font-mono text-lg">{scan.progress}%</span>
          </div>
          <div className="h-3 bg-dark-700 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary-500 to-accent-cyan"
              initial={{ width: 0 }}
              animate={{ width: `${scan.progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
          <p className="text-sm text-gray-400 mt-3">
            {scan.target_url}을(를) 스캔하고 있습니다...
          </p>
        </div>
      )}
      
      {/* Summary Cards */}
      {scan.status === 'completed' && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div className="card text-center">
            <div className="text-3xl font-bold text-severity-critical">{scan.critical_count}</div>
            <div className="text-sm text-gray-400 mt-1">Critical</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-severity-high">{scan.high_count}</div>
            <div className="text-sm text-gray-400 mt-1">High</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-severity-medium">{scan.medium_count}</div>
            <div className="text-sm text-gray-400 mt-1">Medium</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-severity-low">{scan.low_count}</div>
            <div className="text-sm text-gray-400 mt-1">Low</div>
          </div>
          <div className="card text-center">
            <div className="text-3xl font-bold text-severity-info">{scan.info_count}</div>
            <div className="text-sm text-gray-400 mt-1">Info</div>
          </div>
        </div>
      )}
      
      {/* Scan Info */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Shield className="w-5 h-5 text-primary-400" />
          스캔 정보
        </h2>
        <div className="grid sm:grid-cols-2 gap-4">
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <span className="text-sm text-gray-400">대상 URL</span>
            <a 
              href={scan.target_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 text-white hover:text-primary-400 mt-1"
            >
              {scan.target_url}
              <ExternalLink className="w-4 h-4" />
            </a>
          </div>
          <div className="p-3 bg-dark-700/50 rounded-lg">
            <span className="text-sm text-gray-400">스캔 유형</span>
            <p className="text-white mt-1 capitalize">{scan.scan_type} (깊이: {scan.scan_depth})</p>
          </div>
          {scan.started_at && (
            <div className="p-3 bg-dark-700/50 rounded-lg">
              <span className="text-sm text-gray-400">시작 시간</span>
              <p className="text-white mt-1">
                {format(new Date(scan.started_at), 'PPP p', { locale: ko })}
              </p>
            </div>
          )}
          {scan.completed_at && (
            <div className="p-3 bg-dark-700/50 rounded-lg">
              <span className="text-sm text-gray-400">완료 시간</span>
              <p className="text-white mt-1">
                {format(new Date(scan.completed_at), 'PPP p', { locale: ko })}
              </p>
            </div>
          )}
        </div>
      </div>
      
      {/* Error Message */}
      {scan.status === 'failed' && scan.error_message && (
        <div className="card bg-severity-critical/10 border border-severity-critical/30">
          <h2 className="text-lg font-semibold text-severity-critical mb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            오류 발생
          </h2>
          <p className="text-gray-300 font-mono text-sm">{scan.error_message}</p>
        </div>
      )}
      
      {/* Vulnerabilities List */}
      {scan.status === 'completed' && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">
            발견된 취약점 ({scan.total_vulnerabilities}개)
          </h2>
          
          {vulnLoading ? (
            <div className="card animate-pulse">
              <div className="h-20 bg-dark-700 rounded" />
            </div>
          ) : vulnerabilities.length > 0 ? (
            <div className="space-y-3">
              {vulnerabilities.map((vuln) => (
                <motion.div
                  key={vuln.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="card cursor-pointer"
                  onClick={() => setExpandedVuln(expandedVuln === vuln.id ? null : vuln.id)}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <SeverityBadge severity={vuln.severity} />
                        <h3 className="font-semibold text-white">{vuln.name}</h3>
                      </div>
                      <p className="text-sm text-gray-400 mb-2">{vuln.affected_url}</p>
                      <p className="text-sm text-gray-300 line-clamp-2">{vuln.description}</p>
                    </div>
                    <button className="p-2 text-gray-400 hover:text-white">
                      {expandedVuln === vuln.id ? (
                        <ChevronUp className="w-5 h-5" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                  
                  {expandedVuln === vuln.id && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-4 pt-4 border-t border-dark-600 space-y-4"
                    >
                      {vuln.evidence && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">증거</h4>
                          <pre className="p-3 bg-dark-700 rounded-lg text-sm text-gray-300 font-mono overflow-x-auto">
                            {vuln.evidence}
                          </pre>
                        </div>
                      )}
                      
                      {vuln.recommendation && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">권장 조치</h4>
                          <p className="text-sm text-severity-low whitespace-pre-line">
                            {vuln.recommendation}
                          </p>
                        </div>
                      )}
                      
                      {vuln.cwe_id && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">참조</h4>
                          <a 
                            href={`https://cwe.mitre.org/data/definitions/${vuln.cwe_id.replace('CWE-', '')}.html`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-sm text-primary-400 hover:underline"
                          >
                            {vuln.cwe_id}
                          </a>
                        </div>
                      )}
                    </motion.div>
                  )}
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="card text-center py-12">
              <Shield className="w-12 h-12 text-severity-low mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                취약점이 발견되지 않았습니다
              </h3>
              <p className="text-gray-400">
                축하합니다! 스캔 결과 보안 취약점이 감지되지 않았습니다.
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

