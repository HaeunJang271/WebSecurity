import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Shield, 
  Zap, 
  FileText, 
  Code2, 
  ArrowRight,
  CheckCircle,
  Globe,
  Lock
} from 'lucide-react'

const features = [
  {
    icon: Zap,
    title: 'AI 기반 스마트 스캐닝',
    description: '머신러닝을 활용한 지능형 취약점 탐지로 더 정확한 보안 분석을 제공합니다.'
  },
  {
    icon: Globe,
    title: 'OWASP Top 10 지원',
    description: 'SQL Injection, XSS, CSRF 등 주요 웹 취약점을 자동으로 탐지합니다.'
  },
  {
    icon: FileText,
    title: '상세 보고서 생성',
    description: 'PDF/HTML 형식의 전문적인 보안 보고서를 자동으로 생성합니다.'
  },
  {
    icon: Code2,
    title: 'API 연동 지원',
    description: 'CI/CD 파이프라인과 쉽게 연동하여 DevSecOps를 구현할 수 있습니다.'
  },
]

const stats = [
  { value: '99.9%', label: '탐지 정확도' },
  { value: '< 5분', label: '평균 스캔 시간' },
  { value: '100+', label: '취약점 유형' },
  { value: '24/7', label: '서비스 가용성' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-grid">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 glass border-b border-white/5">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary-500 to-accent-cyan flex items-center justify-center">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold text-gradient">SecureScan</span>
            </div>
            
            <div className="flex items-center gap-4">
              <Link 
                to="/login" 
                className="text-gray-300 hover:text-white transition-colors font-medium"
              >
                로그인
              </Link>
              <Link 
                to="/register" 
                className="btn btn-primary"
              >
                무료로 시작하기
              </Link>
            </div>
          </div>
        </div>
      </nav>
      
      {/* Hero Section */}
      <section className="pt-32 pb-20 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-500/10 text-primary-400 text-sm font-medium mb-6">
              <Lock className="w-4 h-4" />
              AI 기반 웹 보안 솔루션
            </span>
            
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-white mb-6 leading-tight">
              웹사이트 보안
              <br />
              <span className="text-gradient">취약점을 찾아드립니다</span>
            </h1>
            
            <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10">
              SecureScan은 AI 기반 자동화 보안 스캐너로,<br />
              여러분의 웹사이트를 안전하게 보호합니다.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link to="/register" className="btn btn-primary text-lg px-8 py-4">
                무료로 스캔 시작하기
                <ArrowRight className="w-5 h-5" />
              </Link>
              <Link to="/login" className="btn btn-secondary text-lg px-8 py-4">
                로그인
              </Link>
            </div>
          </motion.div>
          
          {/* Hero Visual */}
          <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mt-16 relative"
          >
            <div className="absolute inset-0 bg-gradient-to-t from-dark-950 via-transparent to-transparent z-10" />
            <div className="glass rounded-2xl p-8 max-w-4xl mx-auto glow-primary">
              <div className="bg-dark-900 rounded-xl p-6">
                {/* Mock Dashboard */}
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-3 h-3 rounded-full bg-severity-critical" />
                  <div className="w-3 h-3 rounded-full bg-severity-medium" />
                  <div className="w-3 h-3 rounded-full bg-severity-low" />
                </div>
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-dark-800 rounded-lg p-4 text-center">
                    <div className="text-3xl font-bold text-severity-critical">3</div>
                    <div className="text-xs text-gray-500 mt-1">Critical</div>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-4 text-center">
                    <div className="text-3xl font-bold text-severity-high">7</div>
                    <div className="text-xs text-gray-500 mt-1">High</div>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-4 text-center">
                    <div className="text-3xl font-bold text-severity-medium">12</div>
                    <div className="text-xs text-gray-500 mt-1">Medium</div>
                  </div>
                  <div className="bg-dark-800 rounded-lg p-4 text-center">
                    <div className="text-3xl font-bold text-severity-low">5</div>
                    <div className="text-xs text-gray-500 mt-1">Low</div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>
      
      {/* Stats Section */}
      <section className="py-16 px-4 border-y border-white/5">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="text-4xl font-bold text-gradient mb-2">{stat.value}</div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              강력한 보안 기능
            </h2>
            <p className="text-gray-400 max-w-2xl mx-auto">
              SecureScan은 최신 보안 기술을 활용하여 다양한 웹 취약점을 탐지합니다.
            </p>
          </motion.div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.5, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="card card-hover"
                >
                  <div className="w-12 h-12 rounded-xl bg-primary-500/10 flex items-center justify-center mb-4">
                    <Icon className="w-6 h-6 text-primary-400" />
                  </div>
                  <h3 className="text-lg font-semibold text-white mb-2">
                    {feature.title}
                  </h3>
                  <p className="text-gray-400 text-sm">
                    {feature.description}
                  </p>
                </motion.div>
              )
            })}
          </div>
        </div>
      </section>
      
      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            viewport={{ once: true }}
            className="glass rounded-3xl p-8 sm:p-12 text-center glow-primary"
          >
            <h2 className="text-3xl sm:text-4xl font-bold text-white mb-4">
              지금 바로 시작하세요
            </h2>
            <p className="text-gray-400 mb-8 max-w-xl mx-auto">
              무료 계정으로 웹사이트 보안 점검을 시작하세요.
              복잡한 설정 없이 URL만 입력하면 됩니다.
            </p>
            
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-8">
              <Link to="/register" className="btn btn-primary text-lg px-8 py-4">
                무료로 시작하기
                <ArrowRight className="w-5 h-5" />
              </Link>
            </div>
            
            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-gray-400">
              <span className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary-400" />
                신용카드 불필요
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary-400" />
                무료 스캔 제공
              </span>
              <span className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-primary-400" />
                즉시 결과 확인
              </span>
            </div>
          </motion.div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="border-t border-white/5 py-12 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-accent-cyan flex items-center justify-center">
                <Shield className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-bold text-gradient">SecureScan</span>
            </div>
            
            <p className="text-gray-500 text-sm">
              © 2025 SecureScan. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

