from __future__ import annotations

from fastapi import FastAPI, HTTPException, Response

from .catalog import JsonCatalog, UnknownItemError
from .models import CatalogIssue, ItemDetail, ItemSummary


def create_app(catalog: JsonCatalog) -> FastAPI:
    """読み取り専用のViewer APIを作る。"""

    app = FastAPI(title="__VIEWER_PROJECT_NAME__")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/items", response_model=list[ItemSummary])
    def list_items(response: Response) -> list[ItemSummary]:
        response.headers["Cache-Control"] = "no-store"
        return catalog.list_items()

    @app.get("/api/items/{item_id}", response_model=ItemDetail)
    def get_item(item_id: str) -> ItemDetail:
        try:
            return catalog.get_item(item_id)
        except UnknownItemError as error:
            raise HTTPException(status_code=404, detail="Itemが見つかりません") from error

    @app.get("/api/issues", response_model=list[CatalogIssue])
    def list_issues(response: Response) -> list[CatalogIssue]:
        response.headers["Cache-Control"] = "no-store"
        return catalog.list_issues()

    return app
