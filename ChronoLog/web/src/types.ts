export interface Summary {
    error_count: number;
    warning_count: number;
    timeline_count: number;
    unique_messages: number;
    latency_metrics: {
        count: number;
        average: number;
    };
}

export interface TimelineEvent {
    id: number;
    time: string;
    event: string;
    msg_id?: number;
    msg_values?: string[];
    value?: number;
    template?: string;
    msg?: string;
    total_count?: number;
}

export interface TimeseriesPoint {
    time: string;
    value: number;
}

export type MessageTemplates = Record<string, string>;

export interface PagedTimeline {
    events: TimelineEvent[];
    page: number;
    per_page: number;
    total: number; // Inferred from Summary or added to API later, but existing demo uses Summary.timeline_count
}
