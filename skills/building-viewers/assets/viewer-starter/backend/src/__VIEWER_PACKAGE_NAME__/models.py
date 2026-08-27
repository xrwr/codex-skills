from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ItemSummary(BaseModel):
    """一覧へ返す軽量item。"""

    id: str
    name: str
    kind: str
    status: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ItemDetail(ItemSummary):
    """選択itemだけに返す詳細。"""

    description: str = ""
    metrics: dict[str, float | int | str | None] = Field(default_factory=dict)
    preview: dict[str, Any] = Field(default_factory=dict)


class CatalogIssue(BaseModel):
    """隔離したrecordの安全な説明。"""

    item_id: str
    message: str
    severity: str = "error"
