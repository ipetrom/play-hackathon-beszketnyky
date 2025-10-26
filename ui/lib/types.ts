export interface Report {
  id: string
  title: string
  status: string
  createdAt: string
  hasDiff: boolean
  category?: string
  impact?: {
    level: "Low" | "Medium" | "High" | "Critical"
    description: string
  }
  date?: string
  source?: string
  summary?: string
  url?: string
  tags?: string[]
  user_email?: string
  path_to_report?: string
  report_alerts_tips_json_path?: string
}

export interface ReportFilters {
  dateRange: string
  category: string
  impact: string
}

export interface ReportDiffData {
  page: string
  before: {
    title: string
    content: string
    price?: string
    features?: string[]
  }
  after: {
    title: string
    content: string
    price?: string
    features?: string[]
  }
  changes: {
    type: "added" | "removed" | "modified"
    field: string
    before?: string
    after?: string
  }[]
  highlights?: string[]
}

export interface ReportDetail {
  id: string
  title: string
  category: string
  impact: {
    level: "Low" | "Medium" | "High" | "Critical"
    description: string
    score: number
  }
  createdAt: string
  deadline?: string
  summary: string
  body: string
  entities: string[]
  sources: {
    label: string
    url: string
  }[]
  metadataJson: string
  hasDiff: boolean
  diff?: ReportDiffData
}

export interface ChatMessage {
  id: string
  reportId: string
  role: "user" | "assistant"
  content: string
  createdAt: string
}
