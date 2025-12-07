import type { Summary, TimelineEvent, TimeseriesPoint, MessageTemplates } from "../types";

const API_BASE = "/api";

async function fetchJSON<T>(path: string): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) {
        throw new Error(`Failed to fetch ${path}: ${res.statusText}`);
    }
    return res.json();
}

export const api = {
    getSummary: () => fetchJSON<Summary>("/summary"),

    getTimeline: async (page: number = 1, per_page: number = 30, type?: string): Promise<TimelineEvent[]> => {
        const query = new URLSearchParams({
            page: String(page),
            per_page: String(per_page),
            ...(type && { type }),
        });
        return fetchJSON<TimelineEvent[]>(`/timeline?${query.toString()}`);
    },

    getTimeseries: (metric: string, limit: number = 500) =>
        fetchJSON<TimeseriesPoint[]>(`/timeseries?metric=${encodeURIComponent(metric)}&limit=${limit}`),

    getMessages: () => fetchJSON<MessageTemplates>("/messages"),
};
