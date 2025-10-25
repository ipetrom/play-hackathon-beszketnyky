"use client"

import { useRouter } from "next/navigation"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronLeft, ChevronRight } from "lucide-react"
import type { Report } from "@/lib/types"

interface ReportsTableProps {
  reports: Report[]
  isLoading: boolean
  page: number
  pageSize: number
  onPageChange: (page: number) => void
  onPageSizeChange: (pageSize: number) => void
}

export function ReportsTable({
  reports,
  isLoading,
  page,
  pageSize,
  onPageChange,
  onPageSizeChange,
}: ReportsTableProps) {
  const router = useRouter()

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6">
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (reports.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">No reports found</p>
          <p className="text-sm text-muted-foreground mt-2">Try adjusting your filters</p>
        </CardContent>
      </Card>
    )
  }


  const paginatedReports = reports.slice((page - 1) * pageSize, page * pageSize)
  const totalPages = Math.ceil(reports.length / pageSize)

  return (
    <div className="space-y-4">
      {/* Desktop Table */}
      <Card className="hidden md:block">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Title</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedReports.map((report) => (
              <TableRow
                key={report.id}
                className="cursor-pointer hover:bg-muted/50"
                onClick={() => router.push(`/reports/${report.id}`)}
              >
                <TableCell className="font-medium max-w-md">
                  <div className="flex items-center gap-2">
                    {report.title}
                    {report.hasDiff && (
                      <Badge variant="outline" className="text-xs">
                        Diff
                      </Badge>
                    )}
                  </div>
                </TableCell>
                <TableCell>{report.status}</TableCell>
                <TableCell className="text-muted-foreground">
                  {new Date(report.createdAt).toLocaleDateString()}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      router.push(`/reports/${report.id}`)
                    }}
                  >
                    Open
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {/* Mobile Cards */}
      <div className="md:hidden space-y-4">
        {paginatedReports.map((report) => (
          <Card
            key={report.id}
            className="cursor-pointer hover:bg-muted/50 transition-colors"
            onClick={() => router.push(`/reports/${report.id}`)}
          >
            <CardContent className="p-4 space-y-3">
              <div className="flex items-start justify-between gap-2">
                <h3 className="font-medium text-balance flex-1">{report.title}</h3>
                {report.hasDiff && (
                  <Badge variant="outline" className="text-xs">
                    Diff
                  </Badge>
                )}
              </div>

              <div className="flex flex-wrap gap-2">
                <Badge variant="secondary">{report.status}</Badge>
              </div>

              <div className="flex items-center justify-between text-sm text-muted-foreground">
                <span>{new Date(report.createdAt).toLocaleDateString()}</span>
              </div>

              <Button size="sm" className="w-full">
                Open Report
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Pagination */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">Rows per page:</span>
          <Select
            value={pageSize.toString()}
            onValueChange={(value) => {
              onPageSizeChange(Number(value))
              onPageChange(1)
            }}
          >
            <SelectTrigger className="w-20">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="10">10</SelectItem>
              <SelectItem value="25">25</SelectItem>
              <SelectItem value="50">50</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <div className="flex gap-1">
            <Button variant="outline" size="icon" onClick={() => onPageChange(page - 1)} disabled={page === 1}>
              <ChevronLeft className="h-4 w-4" />
              <span className="sr-only">Previous page</span>
            </Button>
            <Button variant="outline" size="icon" onClick={() => onPageChange(page + 1)} disabled={page === totalPages}>
              <ChevronRight className="h-4 w-4" />
              <span className="sr-only">Next page</span>
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
