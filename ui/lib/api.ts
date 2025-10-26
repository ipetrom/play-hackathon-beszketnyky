const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export interface PipelineRunResponse {
  status: string
  message: string
  domain_reports: Record<string, any>
  final_tips_alerts: {
    tips: string[]
    alerts: Array<{
      alert: string
      alert_level: number
    }>
  }
  storage_result: {
    status: string
    storage_paths: {
      merged_summary: string
      tips_alerts: string
      domain_reports: Record<string, string>
    }
    report_id: string
    timestamp: string
  }
  timestamp: string
}

export async function runPipeline(userEmail: string): Promise<PipelineRunResponse> {
  const params = new URLSearchParams({
    user_email: userEmail,
    domains: 'prawo,polityka,financial'
  })
  
  const response = await fetch(`${API_BASE_URL}/pipeline/run?${params}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export async function getUserReports(userEmail: string): Promise<any[]> {
  const response = await fetch(`${API_BASE_URL}/users/${encodeURIComponent(userEmail)}/reports`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  const data = await response.json()
  return data.reports || []
}

export async function getAllReports(status?: string, limit: number = 50, offset: number = 0): Promise<any> {
  const params = new URLSearchParams()
  if (status) params.set('status', status)
  params.set('limit', limit.toString())
  params.set('offset', offset.toString())
  
  const response = await fetch(`${API_BASE_URL}/reports?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}

export async function getReportDetail(reportId: string): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/reports/${encodeURIComponent(reportId)}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}))
    throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
  }

  return response.json()
}
