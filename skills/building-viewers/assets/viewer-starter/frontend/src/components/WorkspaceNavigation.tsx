export function WorkspaceNavigation({
  collapsed,
  onToggle,
}: {
  collapsed: boolean;
  onToggle: () => void;
}) {
  return (
    <header className={collapsed ? "workspace-navigation collapsed" : "workspace-navigation"}>
      <span className="toggle-slot">
        <button
          aria-expanded={!collapsed}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="sidebar-toggle"
          onClick={onToggle}
          type="button"
        >
          <svg aria-hidden="true" viewBox="0 0 16 16">
            <rect height="11" rx="2" width="13" x="1.5" y="2.5" />
            <path d="M5.5 3v10" />
          </svg>
        </button>
      </span>
      <a className="workspace-brand" href="/data">
        <span aria-hidden="true" className="brand-mark">VB</span>
        <span>
          <strong>__VIEWER_PROJECT_NAME__</strong>
          <small>Read-only workspace</small>
        </span>
      </a>
      <nav aria-label="Workspace" className="workspace-links">
        <a aria-current="page" href="/data">Data</a>
      </nav>
      <span className="workspace-context">Viewer</span>
    </header>
  );
}
