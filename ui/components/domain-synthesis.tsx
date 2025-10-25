"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, FileText, AlertTriangle, Lightbulb } from "lucide-react"
import { getReportDetail } from "@/lib/api"
import { MarkdownRenderer } from "@/components/markdown-renderer"

interface DomainSynthesisProps {
  reportId: string
  reportData?: any
}

export function DomainSynthesis({ reportId, reportData }: DomainSynthesisProps) {
  const [domainData, setDomainData] = useState<{
    prawo?: string
    polityka?: string
    financial?: string
  }>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDomainSynthesis()
  }, [reportId])

  const loadDomainSynthesis = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // For now, we'll simulate loading domain synthesis
      // In a real implementation, you would load the actual synthesis files from storage
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Simulate domain synthesis content
      setDomainData({
        prawo: `# Law Domain Report

## Executive Summary
Below are the key updates from the last week relevant to Poland's telecommunications law, UKE, UOKiK, and related regulatory developments impacting the telecom industry.

**Key Points:**
- No new legislative changes or amendments to the Electronic Communications Law (ECL) reported last week
- UKE's ongoing role and recent activities continue to implement ECL provisions
- UOKiK updates show no specific new actions related to telecommunications
- Emerging compliance and business risks require ongoing attention

**Affected Areas:**
- Infrastructure deployment and spectrum management
- Consumer rights and contract management
- Competition and market regulation

**Business Actions Required:**
- Continue monitoring UKE communications for regulatory decisions
- Maintain compliance with ECL requirements
- Review consumer-facing documentation and processes`,
        
        polityka: `# Political Domain Report

## Executive Summary
Recent political developments affecting Poland's telecommunications sector show ongoing consultations and regulatory updates.

**Key Developments:**
- Public consultations on broadband "white spots" continue
- Wholesale market regulation updates from UKE
- Ongoing implementation of new Electronic Communications Law
- Consultations on GIA implementation in telecom law

**Affected Areas:**
- Infrastructure deployment and rural connectivity
- Wholesale regulation and competition
- Consumer rights and compliance
- Administrative procedures and permitting

**Strategic Implications:**
- Monitor consultation outcomes for coverage obligations
- Assess competitive landscape changes
- Prepare for potential regulatory shifts
- Stay informed about infrastructure investment opportunities`,
        
        financial: `# Financial Domain Report

## Executive Summary
Financial performance updates for Poland's telecommunications market show strong growth and continued investment in infrastructure.

**Key Financial Highlights:**
- Orange Polska Q3 2025: 9.3% revenue growth year-over-year
- Net income increased by 1.5% to PLN 465 million in H1 2025
- Capital expenditure rose 18.6% to PLN 799 million
- Market revenue grew by 3% in 2024, reaching over PLN 44.4 billion

**Market Trends:**
- Continued focus on fiber and 5G infrastructure investments
- Strong performance in retail services and convergence bundles
- IT & integration services showing significant growth
- EU-subsidized projects driving network expansion

**Strategic Recommendations:**
- Monitor Orange Polska's investment patterns for market insights
- Align financial strategies with rising capital expenditure trends
- Consider infrastructure investment opportunities in underserved areas
- Maintain vigilance for regulatory updates affecting financial performance`
      })
      
    } catch (err) {
      setError('Failed to load domain synthesis data')
      console.error('Error loading domain synthesis:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Loader2 className="h-4 w-4 animate-spin" />
            Loading Domain Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="h-4 bg-muted animate-pulse rounded" />
            ))}
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-4 w-4" />
            Error Loading Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={loadDomainSynthesis} className="mt-4">
            Retry
          </Button>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileText className="h-4 w-4" />
          Domain Analysis
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="prawo" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="prawo" className="flex items-center gap-2">
              <Badge variant="outline">Legal</Badge>
            </TabsTrigger>
            <TabsTrigger value="polityka" className="flex items-center gap-2">
              <Badge variant="outline">Political</Badge>
            </TabsTrigger>
            <TabsTrigger value="financial" className="flex items-center gap-2">
              <Badge variant="outline">Financial</Badge>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="prawo" className="mt-4">
            <MarkdownRenderer 
              content={domainData.prawo || 'No legal analysis available'} 
            />
          </TabsContent>
          
          <TabsContent value="polityka" className="mt-4">
            <MarkdownRenderer 
              content={domainData.polityka || 'No political analysis available'} 
            />
          </TabsContent>
          
          <TabsContent value="financial" className="mt-4">
            <MarkdownRenderer 
              content={domainData.financial || 'No financial analysis available'} 
            />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
