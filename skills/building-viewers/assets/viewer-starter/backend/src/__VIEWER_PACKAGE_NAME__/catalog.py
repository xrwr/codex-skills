from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from .models import CatalogIssue, ItemDetail, ItemSummary


class UnknownItemError(KeyError):
    """未知のopaque item ID。"""


class JsonCatalog:
    """小さなJSON fixtureを読む差し替え可能なcatalog。"""

    def __init__(self, data_root: Path) -> None:
        self.data_root = Path(data_root).resolve()
        self._items: dict[str, ItemDetail] = {}
        self._issues: list[CatalogIssue] = []
        self._load()

    def _load(self) -> None:
        """record単位で検証し、壊れたrecordだけを隔離する。"""

        catalog_file = self.data_root / "items.json"
        try:
            payload = json.loads(catalog_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            self._issues.append(
                CatalogIssue(item_id="catalog", message="Catalogを読み込めません")
            )
            return
        if not isinstance(payload, list):
            self._issues.append(
                CatalogIssue(item_id="catalog", message="Catalogは配列である必要があります")
            )
            return
        for index, record in enumerate(payload, start=1):
            issue_id = f"record-{index}"
            try:
                item = ItemDetail.model_validate(record)
                if not item.id.strip() or item.id in self._items:
                    raise ValueError("item IDが空または重複しています")
            except (TypeError, ValueError, ValidationError):
                self._issues.append(
                    CatalogIssue(item_id=issue_id, message="Recordを読み込めません")
                )
                continue
            self._items[item.id] = item

    def list_items(self) -> list[ItemSummary]:
        return [
            ItemSummary.model_validate(item.model_dump())
            for item in self._items.values()
        ]

    def get_item(self, item_id: str) -> ItemDetail:
        try:
            return self._items[item_id]
        except KeyError as error:
            raise UnknownItemError(item_id) from error

    def list_issues(self) -> list[CatalogIssue]:
        return list(self._issues)
