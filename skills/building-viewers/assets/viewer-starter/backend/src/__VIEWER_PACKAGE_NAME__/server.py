from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI

from .app import create_app
from .catalog import JsonCatalog


def resolve_data_root() -> Path:
    """環境変数または同梱fixtureからdata rootを決める。"""

    configured = os.environ.get("VIEWER_DATA_DIR")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / "example-data"


def create_runtime_app() -> FastAPI:
    """uvicornから呼び出すruntime app factory。"""

    return create_app(JsonCatalog(resolve_data_root()))
