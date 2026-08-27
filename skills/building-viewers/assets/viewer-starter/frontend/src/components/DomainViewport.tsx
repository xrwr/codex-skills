import type { ItemDetail } from "../api";


export function DomainViewport({ detail }: { detail: ItemDetail }) {
  const values = Array.isArray(detail.preview.values)
    ? detail.preview.values.join(", ")
    : null;

  return (
    <section className="viewport-card">
      <div className="viewport-heading">
        <span>{detail.kind}</span>
        <span className={`status status-${detail.status}`}>{detail.status}</span>
      </div>
      <div className="domain-viewport">
        <p className="viewport-kicker">DOMAIN VIEWPORT</p>
        <h1>{detail.name}</h1>
        {values ? <output>{values}</output> : <p>Replace this panel with the domain renderer.</p>}
      </div>
    </section>
  );
}
