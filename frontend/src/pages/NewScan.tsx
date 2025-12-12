import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Globe, 
  Zap, 
  Shield, 
  Settings,
  ArrowRight,
  AlertCircle,
  Info
} from 'lucide-react'
import toast from 'react-hot-toast'
import { scanAPI } from '../services/api'

const scanTypes = [
  {
    id: 'quick',
    name: '빠른 스캔',
    description: '주요 취약점만 빠르게 검사합니다 (약 1-2분)',
    icon: Zap,
    depth: 1,
  },
  {
    id: 'full',
    name: '전체 스캔',
    description: '모든 페이지를 심층적으로 검사합니다 (약 5-10분)',
    icon: Shield,
    depth: 3,
  },
  {
    id: 'custom',
    name: '사용자 정의',
    description: '스캔 깊이와 옵션을 직접 설정합니다',
    icon: Settings,
    depth: 5,
  },
]

export default function NewScan() {
  const navigate = useNavigate()
  
  const [url, setUrl] = useState('')
  const [scanType, setScanType] = useState('full')
  const [customDepth, setCustomDepth] = useState(3)
  const [loading, setLoading] = useState(false)
  const [agreed, setAgreed] = useState(false)
  
  const selectedType = scanTypes.find(t => t.id === scanType)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!url) {
      toast.error('URL을 입력해주세요')
      return
    }
    
    if (!agreed) {
      toast.error('이용약관에 동의해주세요')
      return
    }
    
    // Basic URL validation
    let targetUrl = url
    if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
      targetUrl = 'https://' + targetUrl
    }
    
    try {
      new URL(targetUrl)
    } catch {
      toast.error('유효한 URL을 입력해주세요')
      return
    }
    
    setLoading(true)
    
    try {
      const scan = await scanAPI.create({
        target_url: targetUrl,
        scan_type: scanType,
        scan_depth: scanType === 'custom' ? customDepth : selectedType?.depth || 3,
      })
      
      toast.success('스캔이 시작되었습니다!')
      navigate(`/scan/${scan.id}`)
    } catch (error: any) {
      const message = error.response?.data?.detail || '스캔 시작에 실패했습니다'
      toast.error(message)
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="max-w-2xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">새 스캔 시작</h1>
        <p className="text-gray-400 mt-2">
          스캔할 웹사이트 URL을 입력하고 스캔 옵션을 선택하세요
        </p>
      </div>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* URL Input */}
        <div className="card">
          <label className="block text-sm font-medium text-gray-300 mb-3">
            대상 URL
          </label>
          <div className="relative">
            <Globe className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              className="w-full bg-dark-700 border border-dark-600 rounded-xl py-4 pl-12 pr-4 text-white text-lg placeholder-gray-500 focus:border-primary-500 transition-colors"
            />
          </div>
          <p className="text-sm text-gray-500 mt-2 flex items-center gap-1">
            <Info className="w-4 h-4" />
            반드시 본인 소유 또는 허가받은 웹사이트만 스캔하세요
          </p>
        </div>
        
        {/* Scan Type Selection */}
        <div className="card">
          <label className="block text-sm font-medium text-gray-300 mb-4">
            스캔 유형
          </label>
          <div className="grid gap-3">
            {scanTypes.map((type) => {
              const Icon = type.icon
              const isSelected = scanType === type.id
              
              return (
                <motion.button
                  key={type.id}
                  type="button"
                  onClick={() => setScanType(type.id)}
                  className={`
                    flex items-start gap-4 p-4 rounded-xl border-2 text-left transition-all
                    ${isSelected 
                      ? 'border-primary-500 bg-primary-500/10' 
                      : 'border-dark-600 bg-dark-700/50 hover:border-dark-500'
                    }
                  `}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className={`
                    w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0
                    ${isSelected ? 'bg-primary-500/20' : 'bg-dark-600'}
                  `}>
                    <Icon className={`w-6 h-6 ${isSelected ? 'text-primary-400' : 'text-gray-400'}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className={`font-semibold ${isSelected ? 'text-primary-400' : 'text-white'}`}>
                      {type.name}
                    </h3>
                    <p className="text-sm text-gray-400 mt-0.5">
                      {type.description}
                    </p>
                  </div>
                  <div className={`
                    w-5 h-5 rounded-full border-2 flex-shrink-0 mt-1
                    ${isSelected 
                      ? 'border-primary-500 bg-primary-500' 
                      : 'border-dark-500'
                    }
                  `}>
                    {isSelected && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-full h-full flex items-center justify-center"
                      >
                        <div className="w-2 h-2 bg-white rounded-full" />
                      </motion.div>
                    )}
                  </div>
                </motion.button>
              )
            })}
          </div>
          
          {/* Custom depth slider */}
          {scanType === 'custom' && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-4 pt-4 border-t border-dark-600"
            >
              <div className="flex items-center justify-between mb-2">
                <label className="text-sm font-medium text-gray-300">
                  스캔 깊이
                </label>
                <span className="text-primary-400 font-mono">{customDepth}</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={customDepth}
                onChange={(e) => setCustomDepth(parseInt(e.target.value))}
                className="w-full h-2 bg-dark-600 rounded-lg appearance-none cursor-pointer accent-primary-500"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>얕음</span>
                <span>깊음</span>
              </div>
            </motion.div>
          )}
        </div>
        
        {/* Agreement */}
        <div className="card bg-dark-800/30">
          <label className="flex items-start gap-3 cursor-pointer">
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              className="w-5 h-5 mt-0.5 rounded border-dark-500 bg-dark-700 text-primary-500 focus:ring-primary-500 focus:ring-offset-0"
            />
            <span className="text-sm text-gray-300">
              본인 소유이거나 스캔 권한이 있는 웹사이트만 검사할 것을 동의합니다. 
              무단 스캔은 불법이며, 이로 인한 모든 책임은 사용자에게 있습니다.
            </span>
          </label>
        </div>
        
        {/* Warning */}
        <div className="flex items-start gap-3 p-4 rounded-xl bg-severity-medium/10 border border-severity-medium/30">
          <AlertCircle className="w-5 h-5 text-severity-medium flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="text-severity-medium font-medium">주의사항</p>
            <p className="text-gray-400 mt-1">
              스캔 중 대상 서버에 다수의 요청이 발생할 수 있습니다. 
              프로덕션 환경에서는 사전에 관리자에게 알리는 것을 권장합니다.
            </p>
          </div>
        </div>
        
        {/* Submit */}
        <button
          type="submit"
          disabled={loading || !agreed}
          className="w-full btn btn-primary text-lg py-4 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              스캔 시작하기
              <ArrowRight className="w-5 h-5" />
            </>
          )}
        </button>
      </form>
    </div>
  )
}

