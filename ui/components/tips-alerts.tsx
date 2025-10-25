"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Loader2, Lightbulb, AlertTriangle, TrendingUp, Shield, Clock } from "lucide-react"
import { getReportDetail } from "@/lib/api"

interface TipsAlertsProps {
  reportId: string
  reportData?: any
}

interface Alert {
  alert: string
  alert_level: number
}

interface TipsAlertsData {
  generated_at: string
  tips: string[]
  alerts: Alert[]
  status: string
}

export function TipsAlerts({ reportId, reportData }: TipsAlertsProps) {
  const [tipsAlertsData, setTipsAlertsData] = useState<TipsAlertsData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTipsAlerts()
  }, [reportId])

  const loadTipsAlerts = async () => {
    setIsLoading(true)
    setError(null)
    
    try {
      // Get report detail to access the tips and alerts JSON path
      const reportDetail = await getReportDetail(reportId)
      const jsonPath = reportDetail.report?.report_alerts_tips_json_path
      
      if (!jsonPath) {
        setError("No tips and alerts data available for this report")
        return
      }

      // In a real implementation, you would fetch the JSON from object storage
      // For now, we'll simulate the data structure you provided
      const mockData: TipsAlertsData = {
        generated_at: "2025-10-25T05:54:09.121709",
        tips: [
          "Accelerate 5G SA deployment in urban clusters to match Orange's network leadership, prioritizing spectrum refarming in the 3.5 GHz band to improve coverage and latency for premium subscribers.",
          "Leverage UKE's proposed wholesale deregulation to expand fiber partnerships with local ISPs in underserved areas, reducing capex while increasing Play's broadband footprint and customer acquisition reach.",
          "Introduce dynamic tariff bundles combining 5G mobile, home internet, and entertainment services to compete with Orange's convergence strategy, emphasizing superior customer service and transparent pricing under the new ECL requirements.",
          "Optimize spectrum portfolio by bidding aggressively in upcoming UKE spectrum auctions for 700 MHz and 26 GHz bands to strengthen rural coverage and prepare for future mmWave use cases.",
          "Enhance prepaid customer retention by implementing ECL-mandated balance portability and introducing loyalty rewards for long-term users, reducing churn to T-Mobile and Plus.",
          "Invest in cybersecurity certifications aligned with EU 5G Toolbox and US-Poland 5G security agreement standards to strengthen trust and qualify for public infrastructure tenders.",
          "Develop targeted marketing campaigns in regions where Orange is reducing wholesale access, positioning Play as a reliable alternative with competitive pricing and bundled offers."
        ],
        alerts: [
          {
            alert: "UKE is advancing plans to deregulate wholesale access markets, potentially removing Orange Polska's LLU obligations. This creates both competitive risk and opportunity—Play must act quickly to secure alternative infrastructure partnerships or expand its own fiber reach before market shifts.",
            alert_level: 4
          },
          {
            alert: "Orange Polska's Q3 2025 revenue growth (9.3% YoY) and increased capex in fiber and 5G signal aggressive market expansion. Play must accelerate its own network investment and bundling strategy to avoid losing high-value convergence customers.",
            alert_level: 4
          },
          {
            alert: "Full enforcement of the Electronic Communications Law (ECL) requires immediate updates to customer contracts, pre-contract disclosures, and number porting processes by year-end. Non-compliance risks UOKiK penalties and reputational damage.",
            alert_level: 5
          },
          {
            alert: "Cybersecurity regulations are tightening under EU and bilateral initiatives, with potential vendor restrictions on high-risk equipment. Play must audit its supply chain and ensure compliance to avoid future network deployment delays.",
            alert_level: 3
          }
        ],
        status: "success"
      }

      setTipsAlertsData(mockData)
    } catch (err) {
      console.error("Failed to load tips and alerts:", err)
      setError("Failed to load tips and alerts data")
    } finally {
      setIsLoading(false)
    }
  }

  const getAlertLevelColor = (level: number) => {
    if (level >= 5) return "bg-red-100 text-red-800 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800"
    if (level >= 4) return "bg-orange-100 text-orange-800 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800"
    if (level >= 3) return "bg-yellow-100 text-yellow-800 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800"
    return "bg-blue-100 text-blue-800 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800"
  }

  const getAlertLevelText = (level: number) => {
    if (level >= 5) return "Critical"
    if (level >= 4) return "High"
    if (level >= 3) return "Medium"
    return "Low"
  }

  if (isLoading) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <Loader2 className="h-6 w-6 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading tips and alerts...</p>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <AlertTriangle className="h-6 w-6 text-destructive mx-auto mb-4" />
          <p className="text-destructive">{error}</p>
        </CardContent>
      </Card>
    )
  }

  if (!tipsAlertsData) {
    return (
      <Card>
        <CardContent className="p-6 text-center">
          <p className="text-muted-foreground">No tips and alerts available for this report.</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Strategic Insights
          </CardTitle>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Clock className="h-4 w-4" />
            {new Date(tipsAlertsData.generated_at).toLocaleDateString()}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="tips" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="tips" className="flex items-center gap-2">
              <Lightbulb className="h-4 w-4" />
              Tips ({tipsAlertsData.tips.length})
            </TabsTrigger>
            <TabsTrigger value="alerts" className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4" />
              Alerts ({tipsAlertsData.alerts.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="tips" className="mt-6 space-y-4">
            <div className="grid gap-4">
              {tipsAlertsData.tips.map((tip, index) => (
                <div
                  key={index}
                  className="flex gap-3 p-4 rounded-lg border border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20"
                >
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/40 flex items-center justify-center">
                      <TrendingUp className="h-3 w-3 text-green-600 dark:text-green-400" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-green-900 dark:text-green-100 mb-1">
                      Strategic Tip #{index + 1}
                    </p>
                    <p className="text-sm text-green-800 dark:text-green-200 leading-relaxed">
                      {tip}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="mt-6 space-y-4">
            <div className="grid gap-4">
              {tipsAlertsData.alerts.map((alert, index) => (
                <div
                  key={index}
                  className="flex gap-3 p-4 rounded-lg border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20"
                >
                  <div className="flex-shrink-0 mt-1">
                    <div className="w-6 h-6 rounded-full bg-red-100 dark:bg-red-900/40 flex items-center justify-center">
                      <AlertTriangle className="h-3 w-3 text-red-600 dark:text-red-400" />
                    </div>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <p className="text-sm font-medium text-red-900 dark:text-red-100">
                        Alert #{index + 1}
                      </p>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getAlertLevelColor(alert.alert_level)}`}
                      >
                        {getAlertLevelText(alert.alert_level)} (Level {alert.alert_level})
                      </Badge>
                    </div>
                    <p className="text-sm text-red-800 dark:text-red-200 leading-relaxed">
                      {alert.alert}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}
