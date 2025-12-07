import { useEffect, useState } from "react";
import type { MessageTemplates, TimeseriesPoint } from "@/types";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { LineChart, Line, ResponsiveContainer, YAxis, Tooltip, XAxis } from "recharts";
import { humanizeTemplate } from "@/lib/formatters";

interface MessageMetricsProps {
    templates: MessageTemplates;
}

export function MessageMetrics({ templates }: MessageMetricsProps) {
    const [charts, setCharts] = useState<{ id: string; data: TimeseriesPoint[] }[]>([]);

    useEffect(() => {
        // Load all message metrics in parallel
        const load = async () => {
            const ids = Object.keys(templates);
            const results = await Promise.all(
                ids.map(async id => {
                    try {
                        const data = await api.getTimeseries(`msg_${id}`, 50);
                        if (data && data.length > 0) return { id, data };
                    } catch (e) {
                        return null;
                    }
                    return null;
                })
            );
            setCharts(results.filter((r): r is { id: string, data: TimeseriesPoint[] } => r !== null));
        };
        if (Object.keys(templates).length > 0) {
            load();
        }
    }, [templates]);

    if (charts.length === 0) return null;

    return (
        <Card className="">
            <CardHeader className="pb-2">
                <h3 className="text-lg font-semibold">Message Metrics</h3>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {charts.map(chart => (
                        <Card key={chart.id} className="bg-muted/20 border-none shadow-none min-w-0">
                            <div className="px-3 pt-3 text-xs text-muted-foreground h-8 overflow-hidden text-ellipsis line-clamp-1" title={templates[chart.id]}>
                                {humanizeTemplate(templates[chart.id])}
                            </div>
                            <div className="h-[120px] w-full px-2 pb-2 relative">
                                <div className="absolute inset-0 w-full h-full p-2">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={chart.data}>
                                            <XAxis
                                                dataKey="time"
                                                tick={{ fontSize: 10, fill: 'hsl(var(--muted-foreground))' }}
                                                tickFormatter={(val: string) => val.split(' ')[1] || val}
                                                minTickGap={30}
                                            />
                                            <YAxis width={30} tick={{ fontSize: 10 }} domain={['auto', 'auto']} />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: 'hsl(var(--card))', borderColor: 'hsl(var(--border))', fontSize: '12px' }}
                                                labelStyle={{ display: 'none' }}
                                            />
                                            <Line
                                                type="step"
                                                dataKey="value"
                                                stroke="hsl(var(--primary))"
                                                strokeWidth={1.5}
                                                dot={false}
                                                isAnimationActive={false}
                                            />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
