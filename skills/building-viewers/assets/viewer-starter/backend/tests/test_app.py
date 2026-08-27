from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from __VIEWER_PACKAGE_NAME__.app import create_app
from __VIEWER_PACKAGE_NAME__.catalog import JsonCatalog


def make_client(tmp_path: Path) -> TestClient:
    """一件のitemを持つAPI clientを作る。"""

    (tmp_path / "items.json").write_text(
        json.dumps(
            [
                {
                    "id": "item-1",
                    "name": "Sample one",
                    "kind": "series",
                    "status": "ready",
                    "metadata": {"split": "train"},
                    "description": "Detail",
                    "metrics": {"score": 0.91},
                    "preview": {"type": "values", "values": [1, 2, 3]},
                }
            ]
        ),
        encoding="utf-8",
    )
    return TestClient(create_app(JsonCatalog(tmp_path)))


def test_read_only_api_exposes_summary_detail_and_issues(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    health = client.get("/api/health")
    items = client.get("/api/items")
    detail = client.get("/api/items/item-1")
    issues = client.get("/api/issues")

    assert health.json() == {"status": "ok"}
    assert items.json()[0]["id"] == "item-1"
    assert "description" not in items.json()[0]
    assert detail.json()["description"] == "Detail"
    assert issues.json() == []
    assert items.headers["cache-control"] == "no-store"


def test_unknown_item_is_404_without_path_details(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    response = client.get("/api/items/not-found")

    assert response.status_code == 404
    assert response.json() == {"detail": "Itemが見つかりません"}
    assert str(tmp_path) not in response.text


def test_viewer_does_not_add_write_endpoints(tmp_path: Path) -> None:
    client = make_client(tmp_path)

    assert client.post("/api/items", json={}).status_code == 405
