from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


PACKAGE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}


def parse_args() -> argparse.Namespace:
    """CLI引数を解析する。"""

    parser = argparse.ArgumentParser(
        description="React＋FastAPI Viewer starterを安全に展開します。"
    )
    parser.add_argument("target", type=Path, help="新規作成する出力directory")
    parser.add_argument("--project-name", required=True, help="画面へ表示する名称")
    parser.add_argument(
        "--package-name",
        required=True,
        help="Python package名。英小文字、数字、underscoreだけを使用します。",
    )
    return parser.parse_args()


def validate_inputs(target: Path, project_name: str, package_name: str) -> None:
    """上書きと不正なpackage名を拒否する。"""

    if target.exists():
        raise ValueError(f"出力先はすでに存在します: {target}")
    if not project_name.strip():
        raise ValueError("project nameは空にできません")
    if not PACKAGE_PATTERN.fullmatch(package_name):
        raise ValueError(
            "package nameは英小文字で始め、英小文字・数字・underscoreだけにしてください"
        )


def render_starter(
    template_root: Path,
    target: Path,
    project_name: str,
    package_name: str,
) -> None:
    """starterをcopyし、pathとtextのplaceholderを置換する。"""

    shutil.copytree(template_root, target)
    package_template = target / "backend" / "src" / "__VIEWER_PACKAGE_NAME__"
    package_template.rename(package_template.with_name(package_name))

    replacements = {
        "__VIEWER_PROJECT_NAME__": project_name.strip(),
        "__VIEWER_PACKAGE_NAME__": package_name,
        "__VIEWER_PACKAGE_DASHED__": package_name.replace("_", "-"),
    }
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for source, replacement in replacements.items():
            text = text.replace(source, replacement)
        path.write_text(text, encoding="utf-8")


def main() -> int:
    """CLI entrypoint。"""

    args = parse_args()
    try:
        validate_inputs(args.target, args.project_name, args.package_name)
        skill_root = Path(__file__).resolve().parents[1]
        render_starter(
            skill_root / "assets" / "viewer-starter",
            args.target.resolve(),
            args.project_name,
            args.package_name,
        )
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(f"Viewer starterを作成しました: {args.target.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
