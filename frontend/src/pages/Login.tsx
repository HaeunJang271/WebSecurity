import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Mail, Lock, ArrowRight, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'
import { useAuthStore } from '../stores/authStore'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!email || !password) {
      toast.error('이메일과 비밀번호를 입력해주세요')
      return
    }
    
    setLoading(true)
    
    try {
      const tokenResponse = await authAPI.login({ email, password })
      
      // 먼저 토큰을 저장 (이후 API 호출에서 사용됨)
      const { setTokens } = useAuthStore.getState()
      setTokens(tokenResponse.access_token, tokenResponse.refresh_token)
      
      // 토큰 저장 후 사용자 정보 조회
      const userResponse = await authAPI.me()
      
      // 전체 로그인 상태 업데이트
      login(
        userResponse,
        tokenResponse.access_token,
        tokenResponse.refresh_token
      )
      
      toast.success('로그인 성공!')
      navigate('/dashboard')
    } catch (error: any) {
      console.error('Login error:', error)
      
      let message = '로그인에 실패했습니다'
      
      if (error.response) {
        const detail = error.response.data?.detail
        
        if (typeof detail === 'string') {
          message = detail
        } else if (Array.isArray(detail)) {
          const errors = detail.map((err: any) => err.msg).join(', ')
          message = errors
        }
        
        if (error.response.status === 500) {
          message = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
        }
      } else if (error.request) {
        message = '서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.'
      }
      
      toast.error(message, { duration: 5000 })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-grid flex items-center justify-center px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <Link to="/" className="flex items-center justify-center gap-3 mb-8">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary-500 to-accent-cyan flex items-center justify-center">
            <Shield className="w-7 h-7 text-white" />
          </div>
          <span className="text-2xl font-bold text-gradient">SecureScan</span>
        </Link>
        
        {/* Card */}
        <div className="glass rounded-2xl p-8">
          <h1 className="text-2xl font-bold text-white text-center mb-2">
            로그인
          </h1>
          <p className="text-gray-400 text-center mb-8">
            계정에 로그인하여 스캔을 시작하세요
          </p>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                이메일
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>
            
            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                비밀번호
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-12 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>
            
            {/* Submit */}
            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  로그인
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
          
          {/* Register link */}
          <p className="text-center text-gray-400 mt-6">
            계정이 없으신가요?{' '}
            <Link to="/register" className="text-primary-400 hover:text-primary-300 font-medium">
              회원가입
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

