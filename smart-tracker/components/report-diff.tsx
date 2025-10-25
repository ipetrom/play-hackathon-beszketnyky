import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, TrendingDown, TrendingUp } from "lucide-react"
import type { ReportDiffData } from "@/lib/types"

interface ReportDiffProps {
  diff: ReportDiffData
}

export function ReportDiff({ diff }: ReportDiffProps) {
  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Changes Detected</CardTitle>
          <a
            href={diff.page}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1 text-sm text-primary hover:underline"
          >
            <ExternalLink className="h-3 w-3" />
            View page
          </a>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid md:grid-cols-2 gap-4">
          {/* Before */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm text-muted-foreground">Before</h4>
            <div className="space-y-2 p-4 bg-muted/50 rounded-lg">
              {Object.entries(diff.before).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{key.replace(/_/g, " ")}</span>
                  <span className="font-medium">{value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* After */}
          <div className="space-y-3">
            <h4 className="font-medium text-sm text-muted-foreground">After</h4>
            <div className="space-y-2 p-4 bg-primary/5 rounded-lg border border-primary/20">
              {Object.entries(diff.after).map(([key, value]) => (
                <div key={key} className="flex justify-between items-center">
                  <span className="text-sm capitalize">{key.replace(/_/g, " ")}</span>
                  <span className="font-medium">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Highlights */}
        <div>
          <h4 className="font-medium text-sm mb-3">Key Changes</h4>
          <div className="flex flex-wrap gap-2">
            {diff.highlights.map((highlight, idx) => {
              const isIncrease = highlight.includes("+")
              const isDecrease = highlight.includes("-")

              return (
                <Badge key={idx} variant="secondary" className="gap-1">
                  {isIncrease && <TrendingUp className="h-3 w-3 text-green-600" />}
                  {isDecrease && <TrendingDown className="h-3 w-3 text-red-600" />}
                  {highlight}
                </Badge>
              )
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
