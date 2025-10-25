"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { ArrowLeft, MessageSquare } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ReportsHeader } from "@/components/reports-header"
import { ReportDiff } from "@/components/report-diff"
import { ReportChat } from "@/components/report-chat"
import { DomainSynthesis } from "@/components/domain-synthesis"
import { TipsAlerts } from "@/components/tips-alerts"
import { MarkdownRenderer } from "@/components/markdown-renderer"
import { useToast } from "@/hooks/use-toast"
import type { ReportDetail } from "@/lib/types"
import { mockReportDetails } from "@/lib/mock-data"
import { getReportDetail } from "@/lib/api"

export default function ReportDetailPage() {
  const router = useRouter()
  const params = useParams()
  const { toast } = useToast()
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)
  const [report, setReport] = useState<ReportDetail | null>(null)
  const [domainSynthesis, setDomainSynthesis] = useState<{[key: string]: string}>({})
  const [tipsAlerts, setTipsAlerts] = useState<any>({})
  const [isLoading, setIsLoading] = useState(true)
  const [isChatOpen, setIsChatOpen] = useState(false)

  useEffect(() => {
    // Check if user is authenticated
    const storedUser = localStorage.getItem("user")
    if (!storedUser) {
      router.push("/")
      return
    }
    setUser(JSON.parse(storedUser))
  }, [router])

  useEffect(() => {
    console.log('Report ID from URL params:', params.id)
    fetchReport()
  }, [params.id])

  const fetchReport = async () => {
    setIsLoading(true)
    try {
      // Try to fetch real report from API
      try {
        const apiData = await getReportDetail(params.id as string)
        const apiReport = apiData.report
        
        if (apiReport) {
          // Convert API report to our format
          const convertedReport: ReportDetail = {
            id: apiReport.report_id,
            title: `Report ${new Date(apiReport.report_date).toLocaleDateString()}`,
            category: apiReport.report_domains?.join(', ') || 'Mixed',
            impact: {
              level: apiReport.report_alerts > 0 ? 'High' : 'Medium' as 'Low' | 'Medium' | 'High' | 'Critical',
              description: `${apiReport.report_tips} tips, ${apiReport.report_alerts} alerts`,
              score: apiReport.report_alerts + apiReport.report_tips
            },
            createdAt: apiReport.created_at,
            deadline: undefined,
            summary: `Generated report with ${apiReport.report_tips} tips and ${apiReport.report_alerts} alerts`,
            body: `This report contains analysis across ${apiReport.report_domains?.join(', ')} domains with ${apiReport.report_tips} actionable tips and ${apiReport.report_alerts} alerts for business decision-making.`,
            entities: apiReport.report_domains || [],
            sources: [],
            metadataJson: "",
            hasDiff: false,
            diff: undefined
          }
          
          setReport(convertedReport)
          
          // Set domain synthesis data if available
          console.log('Report detail page - API response domain_synthesis:', apiData.domain_synthesis)
          console.log('Report detail page - domain_synthesis keys:', Object.keys(apiData.domain_synthesis || {}))
          
          if (apiData.domain_synthesis) {
            setDomainSynthesis(apiData.domain_synthesis)
            console.log('Set domain synthesis data:', apiData.domain_synthesis)
          } else {
            console.log('No domain synthesis data in API response')
          }
          
          // Set tips and alerts data if available
          console.log('Report detail page - API response tips_alerts:', apiData.tips_alerts)
          console.log('Report detail page - tips_alerts keys:', Object.keys(apiData.tips_alerts || {}))
          
          if (apiData.tips_alerts) {
            setTipsAlerts(apiData.tips_alerts)
            console.log('Set tips and alerts data:', apiData.tips_alerts)
          } else {
            console.log('No tips and alerts data in API response')
          }
          
          return
        }
      } catch (apiError) {
        console.warn('Failed to fetch API report, falling back to mock data:', apiError)
      }

      // Fallback to mock data
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Find mock report
      const mockReport = mockReportDetails.find((r) => r.id === params.id)
      if (!mockReport) {
        throw new Error("Report not found")
      }

      setReport(mockReport)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load report. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }


  if (!user) {
    return null
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background">
        <ReportsHeader user={user} />
        <main className="container mx-auto px-4 py-6">
          <div className="space-y-4">
            <div className="h-8 w-32 bg-muted animate-pulse rounded" />
            <div className="h-12 w-3/4 bg-muted animate-pulse rounded" />
            <div className="grid lg:grid-cols-3 gap-6">
              <div className="h-96 bg-muted animate-pulse rounded" />
              <div className="lg:col-span-2 space-y-4">
                <div className="h-64 bg-muted animate-pulse rounded" />
                <div className="h-96 bg-muted animate-pulse rounded" />
              </div>
            </div>
          </div>
        </main>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-background">
        <ReportsHeader user={user} />
        <main className="container mx-auto px-4 py-6">
          <Card>
            <CardContent className="py-12 text-center">
              <p className="text-muted-foreground">Report not found</p>
              <Button onClick={() => router.push("/reports")} className="mt-4">
                Back to Reports
              </Button>
            </CardContent>
          </Card>
        </main>
      </div>
    )
  }


  return (
    <div className="min-h-screen bg-background">
      <ReportsHeader user={user} />
      <main className="container mx-auto px-4 py-6">
        <div className="space-y-6">
          <Button variant="ghost" onClick={() => router.push("/reports")} className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            Back to reports
          </Button>

          <div>
            <h1 className="text-3xl font-bold text-balance mb-2">{report.title}</h1>
            <div className="flex flex-wrap gap-2 items-center text-sm text-muted-foreground">
              <span>ID: {report.id}</span>
              <span>•</span>
              <span>Created: {new Date(report.createdAt).toLocaleDateString()}</span>
              {report.deadline && (
                <>
                  <span>•</span>
                  <span className="text-destructive font-medium">
                    Deadline: {new Date(report.deadline).toLocaleDateString()}
                  </span>
                </>
              )}
            </div>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Full Report</CardTitle>
              </CardHeader>
              <CardContent>
                <MarkdownRenderer content={report.body} />
              </CardContent>
            </Card>

            <DomainSynthesis reportId={report.id} reportData={report} domainSynthesis={domainSynthesis} />

            <TipsAlerts reportId={report.id} reportData={report} tipsAlerts={tipsAlerts} />

            {report.hasDiff && report.diff && <ReportDiff diff={report.diff} />}

            <div className="flex justify-center">
              <Button size="lg" className="gap-2" onClick={() => setIsChatOpen(true)}>
                <MessageSquare className="h-5 w-5" />
                Ask about this report
              </Button>
            </div>
          </div>
        </div>
      </main>

      <ReportChat reportId={params.id as string} isOpen={isChatOpen} onClose={() => setIsChatOpen(false)} />
    </div>
  )
}
