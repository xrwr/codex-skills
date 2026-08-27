export type ViewerState = { itemId: string | null };

export function parseViewerState(search: string): ViewerState {
  const query = new URLSearchParams(search);
  return { itemId: query.get("item") };
}

export function serializeViewerState(state: ViewerState): string {
  const query = new URLSearchParams();
  if (state.itemId) query.set("item", state.itemId);
  const encoded = query.toString();
  return encoded ? `?${encoded}` : "";
}
