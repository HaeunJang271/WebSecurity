export type ScanStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export type Severity = 'critical' | 'high' | 'medium' | 'low' | 'info'

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  is_active: boolean
  created_at: string
}

export interface Scan {
  id: number
  target_url: string
  target_domain: string
  scan_type: string
  scan_depth: number
  status: ScanStatus
  progress: number
  total_vulnerabilities: number
  critical_count: number
  high_count: number
  medium_count: number
  low_count: number
  info_count: number
  error_message?: string
  started_at?: string
  completed_at?: string
  created_at: string
}

export interface Vulnerability {
  id: number
  scan_id: number
  vuln_type: string
  name: string
  severity: Severity
  cvss_score?: number
  affected_url: string
  affected_parameter?: string
  http_method: string
  description: string
  evidence?: string
  recommendation?: string
  references?: string[]
  cwe_id?: string
  is_false_positive: number
  detected_at: string
}

export interface ScanListResponse {
  scans: Scan[]
  total: number
  page: number
  page_size: number
}

export interface VulnerabilityListResponse {
  vulnerabilities: Vulnerability[]
  total: number
  critical: number
  high: number
  medium: number
  low: number
  info: number
}

