import { useEffect, useRef, useState } from "react";

import { fetchJson, type CatalogIssue, type ItemDetail, type ItemSummary } from "./api";
import { DomainViewport } from "./components/DomainViewport";
import { Inspector } from "./components/Inspector";
import { WorkspaceNavigation } from "./components/WorkspaceNavigation";
import { parseViewerState, serializeViewerState } from "./viewer-state";


const SIDEBAR_KEY = "__VIEWER_PACKAGE_DASHED__.sidebar-collapsed";

function initialSidebarState(): boolean {
  try {
    return window.localStorage.getItem(SIDEBAR_KEY) === "true";
  } catch {
    return false;
  }
}

export function App() {
  const initialItemId = useRef(parseViewerState(window.location.search).itemId);
  const selectorButtonRef = useRef<HTMLButtonElement>(null);
  const selectorCloseRef = useRef<HTMLButtonElement>(null);
  const [items, setItems] = useState<ItemSummary[]>([]);
  const [issues, setIssues] = useState<CatalogIssue[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<ItemDetail | null>(null);
  const [loadingCatalog, setLoadingCatalog] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [collapsed, setCollapsed] = useState(initialSidebarState);
  const [selectorOpen, setSelectorOpen] = useState(false);

  useEffect(() => {
    const controller = new AbortController();

    Promise.all([
      fetchJson<ItemSummary[]>("/api/items", controller.signal),
      fetchJson<CatalogIssue[]>("/api/issues", controller.signal),
    ])
      .then(([nextItems, nextIssues]) => {
        setItems(nextItems);
        setIssues(nextIssues);
        const requested = initialItemId.current;
        const selection = nextItems.find((item) => item.id === requested)?.id ?? nextItems[0]?.id ?? null;
        setSelectedId(selection);
      })
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Unable to load catalog");
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoadingCatalog(false);
      });

    return () => controller.abort();
  }, []);

  useEffect(() => {
    if (!selectedId) {
      return;
    }

    const controller = new AbortController();
    fetchJson<ItemDetail>(`/api/items/${encodeURIComponent(selectedId)}`, controller.signal)
      .then(setDetail)
      .catch((reason: unknown) => {
        if (!controller.signal.aborted) {
          setError(reason instanceof Error ? reason.message : "Unable to load item");
        }
      })

    const search = serializeViewerState({ itemId: selectedId });
    window.history.replaceState({}, "", `${window.location.pathname}${search}`);

    return () => controller.abort();
  }, [selectedId]);

  useEffect(() => {
    try {
      window.localStorage.setItem(SIDEBAR_KEY, String(collapsed));
    } catch {
      // 保存できない環境でもビューア本体は継続する。
    }
  }, [collapsed]);

  useEffect(() => {
    if (!selectorOpen) return;

    const previousOverflow = document.body.style.overflow;
    const selectorButton = selectorButtonRef.current;
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelectorOpen(false);
    };
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKeyDown);
    selectorCloseRef.current?.focus();
    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
      selectorButton?.focus();
    };
  }, [selectorOpen]);

  if (loadingCatalog) {
    return <main className="center-state">Loading catalog…</main>;
  }

  if (error && items.length === 0) {
    return (
      <main className="center-state error-state">
        <h1>Catalog unavailable</h1>
        <p>{error}</p>
      </main>
    );
  }

  if (items.length === 0) {
    return (
      <main className="center-state">
        <h1>No items</h1>
        <p>The catalog loaded successfully, but it contains no viewable records.</p>
      </main>
    );
  }

  const selected = items.find((item) => item.id === selectedId) ?? items[0];
  const chooseItem = (itemId: string) => {
    setError(null);
    setSelectedId(itemId);
    setSelectorOpen(false);
  };

  return (
    <div className="app-frame">
      <WorkspaceNavigation collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} />
      <div className={collapsed ? "viewer-shell sidebar-collapsed" : "viewer-shell"}>
        <aside className={selectorOpen ? "selector-rail open" : "selector-rail"} aria-label="Item selector">
          <div className="selector-heading">
            <div>
              <p className="section-label">Catalog</p>
              <strong>{items.length} items</strong>
            </div>
            <button aria-label="Close selector" className="selector-close" onClick={() => setSelectorOpen(false)} ref={selectorCloseRef} type="button">×</button>
          </div>
          <div className="item-list">
            {items.map((item) => (
              <button
                aria-current={item.id === selectedId ? "true" : undefined}
                className={item.id === selectedId ? "item-button selected" : "item-button"}
                key={item.id}
                onClick={() => chooseItem(item.id)}
                type="button"
              >
                <span>{item.name}</span>
                <small>{item.kind} · {item.status}</small>
              </button>
            ))}
          </div>
          {issues.length > 0 ? <p className="issue-count">{issues.length} catalog issue{issues.length === 1 ? "" : "s"}</p> : null}
        </aside>

        {selectorOpen ? <button aria-label="Dismiss selector" className="selector-backdrop" onClick={() => setSelectorOpen(false)} type="button" /> : null}

        <main className="viewer-main">
          <div className="mobile-item-bar">
            <button ref={selectorButtonRef} onClick={() => setSelectorOpen(true)} type="button">
              <span>{selected.name}</span>
              <small>Choose item</small>
            </button>
          </div>
          {error ? <p className="inline-error" role="alert">{error}</p> : null}
          {error ? null : detail?.id === selectedId ? <DomainViewport detail={detail} /> : <div className="viewport-loading">Loading item…</div>}
        </main>

        {detail ? <Inspector detail={detail} /> : <aside aria-label="Inspector" className="inspector muted">No detail loaded</aside>}
      </div>
    </div>
  );
}
