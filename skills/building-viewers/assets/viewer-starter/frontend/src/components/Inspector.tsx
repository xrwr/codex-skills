import type { ItemDetail } from "../api";


export function Inspector({ detail }: { detail: ItemDetail }) {
  return (
    <aside aria-label="Inspector" className="inspector">
      <p className="section-label">Inspector</p>
      <p className="description">{detail.description || "No description"}</p>
      <dl>
        {Object.entries(detail.metadata).map(([key, value]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{String(value)}</dd>
          </div>
        ))}
        {Object.entries(detail.metrics).map(([key, value]) => (
          <div key={key}>
            <dt>{key}</dt>
            <dd>{value ?? "—"}</dd>
          </div>
        ))}
      </dl>
    </aside>
  );
}
