import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { TimelineEvent, MessageTemplates } from "@/types";
import { resolveMessage, getEventVariant } from "@/lib/formatters";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Loader2 } from "lucide-react";

interface TimelineProps {
    templates: MessageTemplates;
    totalEvents: number | null;
}

export function Timeline({ templates, totalEvents }: TimelineProps) {
    const [page, setPage] = useState(1);
    const [perPage, setPerPage] = useState(30);
    const [filterType, setFilterType] = useState<string>("all");
    const [events, setEvents] = useState<TimelineEvent[]>([]);
    const [total, setTotal] = useState<number | null>(totalEvents);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            setLoading(true);
            try {
                const typeParam = filterType === "all" ? undefined : filterType;
                const data = await api.getTimeline(page, perPage, typeParam);
                setEvents(data);
                if (data.length > 0 && data[0].total_count !== undefined) {
                    setTotal(data[0].total_count);
                } else if (data.length === 0) {
                    setTotal(0);
                }
            } catch (e) {
                console.error(e);
            } finally {
                setLoading(false);
            }
        };
        load();
    }, [page, perPage, filterType]);

    // Update local total when prop changes, but only if no filter is active (or verify consistency)
    useEffect(() => {
        if (filterType === "all") {
            setTotal(totalEvents);
        }
    }, [totalEvents, filterType]);

    const maxPage = total !== null ? Math.max(1, Math.ceil(total / perPage)) : 1;

    // Reset page when perPage changes
    const onPerPageChange = (val: string) => {
        setPerPage(Number(val));
        setPage(1);
    };

    const onFilterChange = (val: string) => {
        setFilterType(val);
        setPage(1);
    };

    return (
        <Card className="flex flex-col h-full">
            <CardHeader className="flex flex-row items-center justify-between py-4">
                <CardTitle>Timeline</CardTitle>
                <div className="flex items-center space-x-2">
                    <span className="text-sm text-muted-foreground">Per page</span>
                    <Select value={String(perPage)} onValueChange={onPerPageChange}>
                        <SelectTrigger className="w-[80px] h-8">
                            <SelectValue placeholder="30" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="10">10</SelectItem>
                            <SelectItem value="30">30</SelectItem>
                            <SelectItem value="50">50</SelectItem>
                            <SelectItem value="100">100</SelectItem>
                        </SelectContent>
                    </Select>
                    <span className="text-sm text-muted-foreground ml-2">Type</span>
                    <Select value={filterType} onValueChange={onFilterChange}>
                        <SelectTrigger className="w-[100px] h-8">
                            <SelectValue placeholder="All" />
                        </SelectTrigger>
                        <SelectContent>
                            <SelectItem value="all">All</SelectItem>
                            <SelectItem value="error">Error</SelectItem>
                            <SelectItem value="warning">Warning</SelectItem>
                            <SelectItem value="info">Info</SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </CardHeader>
            <CardContent className="flex-1 overflow-hidden flex flex-col gap-4">
                {/* Controls */}
                <div className="flex justify-between items-center">
                    <div className="flex items-center space-x-2">
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => Math.max(1, p - 1))}
                            disabled={page <= 1 || loading}
                        >
                            Prev
                        </Button>
                        <span className="text-sm tabular-nums">
                            Page {page} {total !== null ? `of ${maxPage}` : ''}
                        </span>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setPage(p => p + 1)}
                            disabled={(total !== null && page >= maxPage) || loading}
                        >
                            Next
                        </Button>
                    </div>
                </div>

                {/* List */}
                <div className="flex-1 overflow-auto border rounded-md relative">
                    {loading && (
                        <div className="absolute inset-0 bg-background/50 flex items-center justify-center z-10">
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        </div>
                    )}
                    {events.length === 0 && !loading ? (
                        <div className="p-4 text-center text-muted-foreground">No events found.</div>
                    ) : (
                        <div className="divide-y">
                            {events.map((e, i) => (
                                <div key={`${e.id}-${i}`} className="p-3 text-sm flex gap-3 hover:bg-muted/50 transition-colors">
                                    <div className="shrink-0 text-muted-foreground text-xs pt-1 whitespace-nowrap">
                                        [{e.time}]
                                    </div>
                                    <div className="flex-1 break-words font-mono">
                                        <div className="flex items-center gap-2 mb-1">
                                            {e.event && (
                                                <Badge variant={getEventVariant(e.event)} className="uppercase text-[10px] px-1 py-0 h-4">
                                                    {e.event}
                                                </Badge>
                                            )}
                                        </div>
                                        <span>{resolveMessage(e, templates)}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
