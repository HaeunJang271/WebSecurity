import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Mail, Lock, User, ArrowRight, Eye, EyeOff } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '../services/api'

export default function Register() {
  const navigate = useNavigate()
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  })
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value })
  }
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    // Validation
    if (!formData.email || !formData.username || !formData.password) {
      toast.error('필수 항목을 모두 입력해주세요')
      return
    }
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('비밀번호가 일치하지 않습니다')
      return
    }
    
    if (formData.password.length < 8) {
      toast.error('비밀번호는 8자 이상이어야 합니다')
      return
    }
    
    if (formData.username.length < 3) {
      toast.error('사용자명은 3자 이상이어야 합니다')
      return
    }
    
    setLoading(true)
    
    try {
      await authAPI.register({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        full_name: formData.full_name || undefined,
      })
      
      toast.success('회원가입이 완료되었습니다!')
      navigate('/login')
    } catch (error: any) {
      console.error('Registration error:', error)
      
      let messages: string[] = []
      
      if (error.response) {
        // 서버에서 응답이 온 경우
        const detail = error.response.data?.detail
        
        if (typeof detail === 'string') {
          // 단순 문자열 에러
          messages.push(detail)
        } else if (Array.isArray(detail)) {
          // 여러 개의 에러 메시지 (이미 한국어로 변환됨)
          messages = detail.map((err: any) => {
            if (typeof err === 'string') return err
            return err.msg || '입력값 오류'
          })
        } else if (detail?.message) {
          messages.push(detail.message)
        }
        
        // HTTP 상태 코드별 추가 처리
        if (error.response.status === 500) {
          messages = ['서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.']
        }
      } else if (error.request) {
        // 요청은 보냈지만 응답이 없는 경우 (네트워크 에러)
        messages.push('서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.')
      } else {
        // 요청 설정 중 에러
        messages.push(error.message || '알 수 없는 오류가 발생했습니다')
      }
      
      // 에러가 없으면 기본 메시지
      if (messages.length === 0) {
        messages.push('회원가입에 실패했습니다')
      }
      
      // 각 에러 메시지를 개별 toast로 표시
      messages.forEach((msg, index) => {
        setTimeout(() => {
          toast.error(msg, { duration: 5000 })
        }, index * 200) // 약간의 딜레이로 순차 표시
      })
    } finally {
      setLoading(false)
    }
  }
  
  return (
    <div className="min-h-screen bg-grid flex items-center justify-center px-4 py-12">
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
            회원가입
          </h1>
          <p className="text-gray-400 text-center mb-8">
            무료 계정을 만들고 보안 스캔을 시작하세요
          </p>
          
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                이메일 <span className="text-primary-400">*</span>
              </label>
              <div className="relative">
                <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  placeholder="you@example.com"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>
            
            {/* Username */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                사용자명 <span className="text-primary-400">*</span>
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  placeholder="username"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>
            
            {/* Full Name */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                이름 <span className="text-gray-500">(선택)</span>
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="text"
                  name="full_name"
                  value={formData.full_name}
                  onChange={handleChange}
                  placeholder="홍길동"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
              </div>
            </div>
            
            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                비밀번호 <span className="text-primary-400">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
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
              <p className="text-xs text-gray-500 mt-1">최소 8자 이상</p>
            </div>
            
            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                비밀번호 확인 <span className="text-primary-400">*</span>
              </label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
                <input
                  type="password"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  placeholder="••••••••"
                  className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
                />
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
                  회원가입
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
          
          {/* Login link */}
          <p className="text-center text-gray-400 mt-6">
            이미 계정이 있으신가요?{' '}
            <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">
              로그인
            </Link>
          </p>
        </div>
      </motion.div>
    </div>
  )
}

