"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ReportsHeader } from "@/components/reports-header"
import { ReportsFilters } from "@/components/reports-filters"
import { ReportsTable } from "@/components/reports-table"
import { useToast } from "@/hooks/use-toast"
import type { Report, ReportFilters } from "@/lib/types"
import { runPipeline, getUserReports, getAllReports } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Loader2, FileText } from "lucide-react"

export default function ReportsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)
  const [reports, setReports] = useState<Report[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [filters, setFilters] = useState<ReportFilters>({
    dateRange: searchParams.get("dateRange") || "Last 7d",
    category: searchParams.get("category") || "All",
    impact: searchParams.get("impact") || "All",
  })
  const [page, setPage] = useState(Number(searchParams.get("page")) || 1)
  const [pageSize, setPageSize] = useState(Number(searchParams.get("pageSize")) || 10)

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
    // Update URL with current filters and pagination
    const params = new URLSearchParams()
    if (filters.dateRange !== "Last 7d") params.set("dateRange", filters.dateRange)
    if (filters.category !== "All") params.set("category", filters.category)
    if (filters.impact !== "All") params.set("impact", filters.impact)
    if (page !== 1) params.set("page", page.toString())
    if (pageSize !== 10) params.set("pageSize", pageSize.toString())

    const queryString = params.toString()
    router.replace(`/reports${queryString ? `?${queryString}` : ""}`, { scroll: false })
  }, [filters, page, pageSize, router])

  useEffect(() => {
    fetchReports()
  }, [filters, page, pageSize])

  const fetchReports = async () => {
    setIsLoading(true)
    try {
      // Fetch real reports from API
      const apiData = await getAllReports()
      const apiReports = apiData.reports || []
      
      // Convert API reports to our format
      const convertedReports = apiReports.map((report: any) => ({
        id: report.report_id,
        title: `Report ${new Date(report.report_date).toLocaleDateString()}`,
        status: report.report_status,
        createdAt: report.created_at,
        hasDiff: false,
        category: Array.isArray(report.report_domains) ? report.report_domains.join(', ') : 'Mixed',
        impact: {
          level: report.report_alerts > 0 ? 'High' : 'Medium' as 'Low' | 'Medium' | 'High' | 'Critical',
          description: `${report.report_tips} tips, ${report.report_alerts} alerts`
        },
        date: report.report_date,
        summary: `Generated report with ${report.report_tips} tips and ${report.report_alerts} alerts`,
        user_email: report.user_email,
        path_to_report: report.path_to_report,
        report_alerts_tips_json_path: report.report_alerts_tips_json_path
      }))
      
      // Apply filters
      let filtered = convertedReports
      
      if (filters.category !== "All") {
        filtered = filtered.filter((r: any) => r.category.includes(filters.category))
      }

      if (filters.impact !== "All") {
        filtered = filtered.filter((r: any) => r.impact.level === filters.impact)
      }
      
      setReports(filtered)
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load reports. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleGenerateReport = async () => {
    if (!user?.email) {
      toast({
        title: "Error",
        description: "User email not found. Please try logging in again.",
        variant: "destructive",
      })
      return
    }

    setIsGeneratingReport(true)
    try {
      toast({
        title: "Generating Report",
        description: "Starting report generation... This may take a few minutes.",
      })

      const result = await runPipeline(user.email)
      
      toast({
        title: "Report Generated Successfully!",
        description: `Report created with ${result.final_tips_alerts.tips.length} tips and ${result.final_tips_alerts.alerts.length} alerts.`,
      })

      // Refresh the reports list
      await fetchReports()
    } catch (error) {
      console.error('Report generation failed:', error)
      toast({
        title: "Report Generation Failed",
        description: error instanceof Error ? error.message : "An unexpected error occurred. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsGeneratingReport(false)
    }
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <ReportsHeader user={user} />
      <main className="container mx-auto px-4 py-6 space-y-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-balance mb-2">Reports</h1>
            <p className="text-muted-foreground">Monitor industry changes and regulatory updates in real-time</p>
          </div>
          <Button 
            onClick={handleGenerateReport}
            disabled={isGeneratingReport}
            className="flex items-center gap-2"
          >
            {isGeneratingReport ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <FileText className="h-4 w-4" />
            )}
            {isGeneratingReport ? "Generating..." : "Make a Report"}
          </Button>
        </div>

        <ReportsFilters filters={filters} onFiltersChange={setFilters} />

        <ReportsTable
          reports={reports}
          isLoading={isLoading}
          page={page}
          pageSize={pageSize}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      </main>
    </div>
  )
}
