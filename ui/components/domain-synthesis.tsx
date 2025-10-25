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
  domainSynthesis?: {[key: string]: string}
}

export function DomainSynthesis({ reportId, reportData, domainSynthesis }: DomainSynthesisProps) {
  const [domainData, setDomainData] = useState<{
    prawo?: string
    polityka?: string
    financial?: string
  }>({})
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDomainSynthesis()
  }, [reportId, domainSynthesis])

  const loadDomainSynthesis = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      console.log('DomainSynthesis component - domainSynthesis prop:', domainSynthesis)
      console.log('DomainSynthesis component - domainSynthesis keys:', Object.keys(domainSynthesis || {}))
      
      // Use real domain synthesis data if available
      if (domainSynthesis && Object.keys(domainSynthesis).length > 0) {
        console.log('Using real domain synthesis data')
        setDomainData(domainSynthesis)
        setIsLoading(false)
        return
      }
      
      // If no domain synthesis data is provided, show a message
      setDomainData({
        prawo: 'No legal domain analysis available - the domain synthesis files could not be loaded from storage.',
        polityka: 'No political domain analysis available - the domain synthesis files could not be loaded from storage.', 
        financial: 'No financial domain analysis available - the domain synthesis files could not be loaded from storage.'
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
