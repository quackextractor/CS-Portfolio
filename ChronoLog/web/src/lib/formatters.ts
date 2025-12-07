import type { TimelineEvent, MessageTemplates } from "../types";

export function humanizeTemplate(t?: string): string {
    if (!t) return "";
    // remove typical leading timestamp pattern
    t = t.replace(/^\{num\}-\{num\}-\{num\}\s+\{num\}:\{num\}:\{num\}\s+/, '');
    // replace {num} with ellipsis
    return t.replace(/\{num\}/g, '…');
}

export function interpolateTemplate(t: string | undefined, vals: string[] | undefined): string {
    if (!t) return "";
    let i = 0;
    return t.replace(/\{num\}/g, () => {
        if (Array.isArray(vals) && i < vals.length) {
            const v = vals[i++];
            return String(v);
        }
        i++;
        return '…';
    });
}

export function resolveMessage(e: TimelineEvent, templates: MessageTemplates): string {
    // If msg_id present, use template
    if (e.msg_id !== undefined && templates[String(e.msg_id)] !== undefined) {
        const tpl = templates[String(e.msg_id)];
        if (e.msg_values && e.msg_values.length > 0) {
            return interpolateTemplate(tpl, e.msg_values);
        }
        return humanizeTemplate(tpl);
    }
    // If value present
    if (e.value !== undefined) {
        return String(e.value);
    }
    // Fallback
    return e.msg || "";
}

export function getEventVariant(event: string): "default" | "destructive" | "secondary" | "outline" {
    switch (event?.toLowerCase()) {
        case 'error': return 'destructive';
        case 'warning': return 'secondary'; // yellow-ish usually, but secondary is grey. We might custom style it.
        default: return 'outline';
    }
}
