"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ReportsHeader } from "@/components/reports-header"
import { ReportsFilters } from "@/components/reports-filters"
import { ReportsTable } from "@/components/reports-table"
import { useToast } from "@/hooks/use-toast"
import type { Report, ReportFilters } from "@/lib/types"
import { mockReports } from "@/lib/mock-data"

export default function ReportsPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { toast } = useToast()
  const [user, setUser] = useState<{ name: string; email: string } | null>(null)
  const [reports, setReports] = useState<Report[]>([])
  const [isLoading, setIsLoading] = useState(true)
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
      // TODO: Replace with actual API call
      // const params = new URLSearchParams({
      //   category: filters.category !== 'All' ? filters.category : '',
      //   impact: filters.impact !== 'All' ? filters.impact : '',
      //   from: getDateFromRange(filters.dateRange),
      //   page: page.toString(),
      //   pageSize: pageSize.toString(),
      // })
      // const response = await fetch(`/api/reports?${params}`)
      // const data = await response.json()

      // Mock API delay
      await new Promise((resolve) => setTimeout(resolve, 500))

      // Filter mock data
      let filtered = [...mockReports]

      if (filters.category !== "All") {
        filtered = filtered.filter((r) => r.category === filters.category)
      }

      if (filters.impact !== "All") {
        filtered = filtered.filter((r) => r.impact.level === filters.impact)
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

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-background">
      <ReportsHeader user={user} />
      <main className="container mx-auto px-4 py-6 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-balance mb-2">Reports</h1>
          <p className="text-muted-foreground">Monitor industry changes and regulatory updates in real-time</p>
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
