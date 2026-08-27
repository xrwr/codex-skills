from __future__ import annotations

import json
from pathlib import Path

import pytest

from __VIEWER_PACKAGE_NAME__.catalog import JsonCatalog, UnknownItemError


def write_items(root: Path) -> None:
    """正常itemと壊れたitemを含むfixtureを書く。"""

    root.mkdir(exist_ok=True)
    (root / "items.json").write_text(
        json.dumps(
            [
                {
                    "id": "item-1",
                    "name": "Sample one",
                    "kind": "series",
                    "status": "ready",
                    "metadata": {"split": "train"},
                    "description": "A real detail payload",
                    "metrics": {"score": 0.91},
                    "preview": {"type": "values", "values": [1, 2, 3]},
                },
                {"id": "", "name": "Broken"},
            ]
        ),
        encoding="utf-8",
    )


def test_catalog_keeps_valid_items_when_one_record_is_broken(tmp_path: Path) -> None:
    write_items(tmp_path)

    catalog = JsonCatalog(tmp_path)

    assert [item.id for item in catalog.list_items()] == ["item-1"]
    assert catalog.get_item("item-1").metrics == {"score": 0.91}
    assert len(catalog.list_issues()) == 1
    assert catalog.list_issues()[0].item_id == "record-2"


def test_catalog_rejects_unknown_opaque_id(tmp_path: Path) -> None:
    write_items(tmp_path)
    catalog = JsonCatalog(tmp_path)

    with pytest.raises(UnknownItemError):
        catalog.get_item("../items.json")


def test_catalog_does_not_expose_data_root(tmp_path: Path) -> None:
    write_items(tmp_path)
    catalog = JsonCatalog(tmp_path)

    payload = catalog.get_item("item-1").model_dump_json()

    assert str(tmp_path) not in payload
