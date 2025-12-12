import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Search, Filter, Clock } from 'lucide-react'
import { scanAPI } from '../services/api'
import ScanCard from '../components/ScanCard'
import { ScanStatus, Scan } from '../types'

const statusFilters = [
  { value: '', label: '전체' },
  { value: 'pending', label: '대기 중' },
  { value: 'running', label: '스캔 중' },
  { value: 'completed', label: '완료' },
  { value: 'failed', label: '실패' },
  { value: 'cancelled', label: '취소됨' },
]

export default function ScanHistory() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<ScanStatus | ''>('')
  const [searchQuery, setSearchQuery] = useState('')
  
  const { data, isLoading } = useQuery({
    queryKey: ['scans', 'history', page, statusFilter],
    queryFn: () => scanAPI.list({ 
      page, 
      page_size: 10,
      status: statusFilter || undefined 
    }),
  })
  
  const scans: Scan[] = data?.scans || []
  const total = data?.total || 0
  const totalPages = Math.ceil(total / 10)
  
  // Filter by search query (client-side)
  const filteredScans = searchQuery
    ? scans.filter(s => 
        s.target_domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
        s.target_url.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : scans
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white">스캔 기록</h1>
        <p className="text-gray-400 mt-2">
          총 {total}개의 스캔 기록이 있습니다
        </p>
      </div>
      
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="flex-1 relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="도메인 또는 URL로 검색..."
            className="w-full bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-4 text-white placeholder-gray-500 focus:border-primary-500 transition-colors"
          />
        </div>
        
        {/* Status Filter */}
        <div className="relative">
          <Filter className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value as ScanStatus | '')
              setPage(1)
            }}
            className="appearance-none bg-dark-800 border border-dark-600 rounded-xl py-3 pl-12 pr-10 text-white focus:border-primary-500 transition-colors cursor-pointer"
          >
            {statusFilters.map((filter) => (
              <option key={filter.value} value={filter.value}>
                {filter.label}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      {/* Scans List */}
      {isLoading ? (
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card animate-pulse">
              <div className="h-6 bg-dark-700 rounded w-1/3 mb-4" />
              <div className="h-4 bg-dark-700 rounded w-2/3 mb-4" />
              <div className="h-4 bg-dark-700 rounded w-1/2" />
            </div>
          ))}
        </div>
      ) : filteredScans.length > 0 ? (
        <>
          <div className="space-y-4">
            {filteredScans.map((scan, index) => (
              <ScanCard key={scan.id} scan={scan} index={index} />
            ))}
          </div>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 rounded-lg bg-dark-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-dark-600 transition-colors"
              >
                이전
              </button>
              
              <div className="flex items-center gap-1">
                {[...Array(Math.min(5, totalPages))].map((_, i) => {
                  let pageNum: number
                  if (totalPages <= 5) {
                    pageNum = i + 1
                  } else if (page <= 3) {
                    pageNum = i + 1
                  } else if (page >= totalPages - 2) {
                    pageNum = totalPages - 4 + i
                  } else {
                    pageNum = page - 2 + i
                  }
                  
                  return (
                    <button
                      key={pageNum}
                      onClick={() => setPage(pageNum)}
                      className={`w-10 h-10 rounded-lg transition-colors ${
                        page === pageNum
                          ? 'bg-primary-500 text-white'
                          : 'bg-dark-700 text-gray-400 hover:bg-dark-600'
                      }`}
                    >
                      {pageNum}
                    </button>
                  )
                })}
              </div>
              
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-4 py-2 rounded-lg bg-dark-700 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-dark-600 transition-colors"
              >
                다음
              </button>
            </div>
          )}
        </>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="card text-center py-12"
        >
          <Clock className="w-12 h-12 text-gray-600 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-white mb-2">
            {searchQuery || statusFilter ? '검색 결과가 없습니다' : '스캔 기록이 없습니다'}
          </h3>
          <p className="text-gray-400">
            {searchQuery || statusFilter 
              ? '다른 검색어나 필터를 시도해보세요'
              : '새로운 스캔을 시작해보세요'
            }
          </p>
        </motion.div>
      )}
    </div>
  )
}

