"use client"

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import type { ReportFilters } from "@/lib/types"

interface ReportsFiltersProps {
  filters: ReportFilters
  onFiltersChange: (filters: ReportFilters) => void
}

export function ReportsFilters({ filters, onFiltersChange }: ReportsFiltersProps) {
  return (
    <div className="flex flex-wrap gap-4 p-4 bg-muted/50 rounded-lg border">
      <div className="flex-1 min-w-[200px] space-y-2">
        <Label htmlFor="dateRange">Date Range</Label>
        <Select value={filters.dateRange} onValueChange={(value) => onFiltersChange({ ...filters, dateRange: value })}>
          <SelectTrigger id="dateRange">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="Last 24h">Last 24 hours</SelectItem>
            <SelectItem value="Last 7d">Last 7 days</SelectItem>
            <SelectItem value="Last 30d">Last 30 days</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px] space-y-2">
        <Label htmlFor="category">Category</Label>
        <Select value={filters.category} onValueChange={(value) => onFiltersChange({ ...filters, category: value })}>
          <SelectTrigger id="category">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All Categories</SelectItem>
            <SelectItem value="Prawo">Prawo</SelectItem>
            <SelectItem value="Gov">Gov</SelectItem>
            <SelectItem value="Competition">Competition</SelectItem>
            <SelectItem value="Market">Market</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 min-w-[200px] space-y-2">
        <Label htmlFor="impact">Impact</Label>
        <Select value={filters.impact} onValueChange={(value) => onFiltersChange({ ...filters, impact: value })}>
          <SelectTrigger id="impact">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="All">All Levels</SelectItem>
            <SelectItem value="Low">Low</SelectItem>
            <SelectItem value="Medium">Medium</SelectItem>
            <SelectItem value="High">High</SelectItem>
          </SelectContent>
        </Select>
      </div>
    </div>
  )
}
