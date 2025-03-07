import { fetchFraudData } from "@/lib/data"
import DashboardHeader from "@/components/dashboard-header"
import KpiCards from "@/components/kpi-cards"
import FraudByTransactionType from "@/components/fraud-by-transaction-type"
import DeviceTypeTreemap from "@/components/device-type-treemap"
import FraudHeatmap from "@/components/fraud-heatmap"
import FraudTrendChart from "@/components/fraud-trend-chart"
import FraudDonutChart from "@/components/fraud-donut-chart"
import HighRiskScatterPlot from "@/components/high-risk-scatter-plot"
import DownloadReport from "@/components/download-report"
import DashboardSummary from "@/components/dashboard-summary"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default async function Dashboard() {
  const data = await fetchFraudData()

  return (
    <div className="flex min-h-screen flex-col">
      <DashboardHeader />
      <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
        <div className="flex items-center justify-between">
          <h2 className="text-3xl font-bold tracking-tight">Fraud Analytics Dashboard</h2>
        </div>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analytics">Analytics</TabsTrigger>
            <TabsTrigger value="reports">Reports</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <KpiCards data={data} />

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <FraudByTransactionType data={data} className="col-span-4" />
              <FraudDonutChart data={data} className="col-span-3" />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <FraudTrendChart data={data} className="col-span-4" />
              <DeviceTypeTreemap data={data} className="col-span-3" />
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <FraudHeatmap data={data} className="col-span-4" />
              <HighRiskScatterPlot data={data} className="col-span-3" />
            </div>
          </TabsContent>

          <TabsContent value="analytics" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <FraudTrendChart data={data} className="col-span-7" />
              <FraudHeatmap data={data} className="col-span-7" />
              <HighRiskScatterPlot data={data} className="col-span-7" />
            </div>
          </TabsContent>

          <TabsContent value="reports" className="space-y-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-semibold">Fraud Reports</h3>
              <DownloadReport data={data} />
            </div>

            <DashboardSummary data={data} />

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
              <FraudByTransactionType data={data} className="col-span-7" />
              <DeviceTypeTreemap data={data} className="col-span-7" />
              <FraudDonutChart data={data} className="col-span-7" />
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

