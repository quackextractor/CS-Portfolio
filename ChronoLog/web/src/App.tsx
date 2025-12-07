import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import type { Summary, MessageTemplates } from '@/types';
import { DashboardCharts } from "@/components/DashboardCharts";
import { Timeline } from "@/components/Timeline";
import { MessageMetrics } from "@/components/MessageCharts";
import { Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

function App() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [templates, setTemplates] = useState<MessageTemplates>({});
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [sum, tpls] = await Promise.all([
        api.getSummary(),
        api.getMessages()
      ]);
      setSummary(sum);
      setTemplates(tpls);
    } catch (e) {
      console.error("Failed to load initial data", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-background text-foreground p-6 font-sans antialiased">
      <div className="max-w-[1200px] mx-auto space-y-6">

        <header className="flex items-center justify-between pb-4 border-b">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">ChronoLog</h1>
            <p className="text-muted-foreground">System telemetry and log explorer</p>
          </div>
          <Button variant="outline" onClick={loadData} disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
            Refresh
          </Button>
        </header>

        <main className="space-y-6">
          {/* Charts Row */}
          <DashboardCharts summary={summary} />

          {/* Message Metrics Row */}
          <MessageMetrics templates={templates} />

          {/* Timeline Row */}
          <div className="h-[600px]">
            <Timeline templates={templates} totalEvents={summary?.timeline_count || null} />
          </div>
        </main>

      </div>
    </div>
  );
}

export default App;
