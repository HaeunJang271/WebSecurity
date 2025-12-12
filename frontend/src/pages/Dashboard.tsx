import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Plus,
  TrendingUp,
  Activity
} from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { scanAPI } from '../services/api'
import { useAuthStore } from '../stores/authStore'
import ScanCard from '../components/ScanCard'
import { Scan } from '../types'

const severityColors = {
  critical: '#FF4757',
  high: '#FF6B35',
  medium: '#FFA502',
  low: '#2ED573',
  info: '#00D4AA',
}

export default function Dashboard() {
  const { user } = useAuthStore()
  
  const { data, isLoading } = useQuery({
    queryKey: ['scans', 'dashboard'],
    queryFn: () => scanAPI.list({ page: 1, page_size: 5 }),
  })
  
  const scans: Scan[] = data?.scans || []
  const totalScans = data?.total || 0
  
  // Calculate summary stats
  const completedScans = scans.filter(s => s.status === 'completed')
  const totalVulnerabilities = completedScans.reduce((acc, s) => acc + s.total_vulnerabilities, 0)
  const criticalCount = completedScans.reduce((acc, s) => acc + s.critical_count, 0)
  const highCount = completedScans.reduce((acc, s) => acc + s.high_count, 0)
  
  const pieData = [
    { name: 'Critical', value: criticalCount, color: severityColors.critical },
    { name: 'High', value: highCount, color: severityColors.high },
    { name: 'Medium', value: completedScans.reduce((acc, s) => acc + s.medium_count, 0), color: severityColors.medium },
    { name: 'Low', value: completedScans.reduce((acc, s) => acc + s.low_count, 0), color: severityColors.low },
    { name: 'Info', value: completedScans.reduce((acc, s) => acc + s.info_count, 0), color: severityColors.info },
  ].filter(d => d.value > 0)
  
  const stats = [
    { 
      label: '총 스캔', 
      value: totalScans, 
      icon: Activity, 
      color: 'text-accent-cyan',
      bg: 'bg-accent-cyan/10'
    },
    { 
      label: '발견된 취약점', 
      value: totalVulnerabilities, 
      icon: AlertTriangle, 
      color: 'text-severity-high',
      bg: 'bg-severity-high/10'
    },
    { 
      label: 'Critical/High', 
      value: criticalCount + highCount, 
      icon: Shield, 
      color: 'text-severity-critical',
      bg: 'bg-severity-critical/10'
    },
    { 
      label: '완료된 스캔', 
      value: completedScans.length, 
      icon: CheckCircle, 
      color: 'text-severity-low',
      bg: 'bg-severity-low/10'
    },
  ]
  
  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-white">
            안녕하세요, {user?.username}님! 👋
          </h1>
          <p className="text-gray-400 mt-1">
            오늘도 안전한 하루 보내세요
          </p>
        </div>
        
        <Link to="/scan/new" className="btn btn-primary">
          <Plus className="w-5 h-5" />
          새 스캔 시작
        </Link>
      </div>
      
      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3, delay: index * 0.1 }}
              className="card"
            >
              <div className="flex items-center gap-4">
                <div className={`w-12 h-12 rounded-xl ${stat.bg} flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{stat.value}</p>
                  <p className="text-sm text-gray-400">{stat.label}</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
      
      {/* Main Content */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Recent Scans */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-white">최근 스캔</h2>
            <Link to="/history" className="text-primary-400 hover:text-primary-300 text-sm font-medium">
              전체 보기 →
            </Link>
          </div>
          
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="card animate-pulse">
                  <div className="h-6 bg-dark-700 rounded w-1/3 mb-4" />
                  <div className="h-4 bg-dark-700 rounded w-2/3 mb-4" />
                  <div className="h-4 bg-dark-700 rounded w-1/2" />
                </div>
              ))}
            </div>
          ) : scans.length > 0 ? (
            <div className="space-y-4">
              {scans.map((scan, index) => (
                <ScanCard key={scan.id} scan={scan} index={index} />
              ))}
            </div>
          ) : (
            <div className="card text-center py-12">
              <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-white mb-2">
                아직 스캔 기록이 없습니다
              </h3>
              <p className="text-gray-400 mb-4">
                첫 번째 보안 스캔을 시작해보세요
              </p>
              <Link to="/scan/new" className="btn btn-primary inline-flex">
                <Plus className="w-5 h-5" />
                스캔 시작하기
              </Link>
            </div>
          )}
        </div>
        
        {/* Vulnerability Chart */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-white">취약점 분포</h2>
          
          <div className="card">
            {pieData.length > 0 ? (
              <>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={4}
                        dataKey="value"
                      >
                        {pieData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip
                        contentStyle={{
                          background: '#2c2c2e',
                          border: '1px solid rgba(255,255,255,0.1)',
                          borderRadius: '8px',
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                
                {/* Legend */}
                <div className="space-y-2 mt-4">
                  {pieData.map((item) => (
                    <div key={item.name} className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm text-gray-400">{item.name}</span>
                      </div>
                      <span className="text-sm font-medium text-white">{item.value}</span>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-8">
                <TrendingUp className="w-10 h-10 text-gray-600 mx-auto mb-3" />
                <p className="text-gray-400 text-sm">
                  스캔을 완료하면 취약점 분포가 표시됩니다
                </p>
              </div>
            )}
          </div>
          
          {/* Quick Actions */}
          <div className="card">
            <h3 className="text-sm font-medium text-gray-400 mb-4">빠른 작업</h3>
            <div className="space-y-2">
              <Link 
                to="/scan/new"
                className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
              >
                <Plus className="w-5 h-5 text-primary-400" />
                <span className="text-white">새 스캔 시작</span>
              </Link>
              <Link 
                to="/history"
                className="flex items-center gap-3 p-3 rounded-lg bg-dark-700/50 hover:bg-dark-700 transition-colors"
              >
                <Clock className="w-5 h-5 text-primary-400" />
                <span className="text-white">스캔 기록 보기</span>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

