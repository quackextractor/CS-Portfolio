import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, BarChart, Bar } from 'recharts';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import type { Summary, TimeseriesPoint } from "@/types";
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface DashboardChartsProps {
    summary: Summary | null;
}

export function DashboardCharts({ summary }: DashboardChartsProps) {
    const [latencyData, setLatencyData] = useState<TimeseriesPoint[]>([]);

    useEffect(() => {
        const load = async () => {
            try {
                const data = await api.getTimeseries('latency', 500);
                setLatencyData(data);
            } catch (e) { console.error(e); }
        };
        load();
    }, []);

    const errorCount = summary?.error_count || 0;
    const warningCount = summary?.warning_count || 0;
    const countData = [
        { name: 'Errors', count: errorCount, fill: 'hsl(var(--destructive))' },
        { name: 'Warnings', count: warningCount, fill: 'hsl(var(--chart-4))' },
    ];

    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card className="min-w-0">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Latency (Last 500)</CardTitle>
                </CardHeader>
                <CardContent className="h-[250px] p-0 relative min-w-0">
                    <div className="absolute inset-0 w-full h-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={latencyData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(var(--border))" />
                                <XAxis
                                    dataKey="time"
                                    tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                                    tickFormatter={(val: string) => val.split(' ')[1] || val}
                                    minTickGap={30}
                                />
                                <YAxis
                                    tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                                    width={40}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '6px' }}
                                />
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="hsl(var(--primary))"
                                    strokeWidth={2}
                                    dot={false}
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>

            <Card className="min-w-0">
                <CardHeader className="pb-2">
                    <CardTitle className="text-sm font-medium">Event Counts</CardTitle>
                </CardHeader>
                <CardContent className="h-[250px] p-0 relative min-w-0">
                    <div className="absolute inset-0 w-full h-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={countData} layout="vertical" margin={{ left: 20 }}>
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="hsl(var(--border))" />
                                <XAxis type="number" tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }} />
                                <YAxis
                                    dataKey="name"
                                    type="category"
                                    width={60}
                                    tick={{ fontSize: 12, fill: 'hsl(var(--muted-foreground))' }}
                                />
                                <Tooltip
                                    contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', borderRadius: '6px' }}
                                    cursor={{ fill: 'hsl(var(--muted)/0.2)' }}
                                />
                                <Bar dataKey="count" radius={[0, 4, 4, 0]} barSize={32} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
