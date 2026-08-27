export type ItemSummary = {
  id: string;
  name: string;
  kind: string;
  status: string;
  metadata: Record<string, unknown>;
};

export type ItemDetail = ItemSummary & {
  description: string;
  metrics: Record<string, number | string | null>;
  preview: Record<string, unknown>;
};

export type CatalogIssue = {
  item_id: string;
  message: string;
  severity: string;
};

export async function fetchJson<T>(url: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(url, { signal });
  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
}
