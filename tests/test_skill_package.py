from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "building-viewers"
SUMMARIZING_EXPERIMENTS_SKILL_ROOT = REPOSITORY_ROOT / "skills" / "summarizing-experiments"


class SkillPackageTest(unittest.TestCase):
    """配布形式と同梱ツールを検査する。エージェントの判断品質は別途確認する。"""

    def test_repository_has_reproducible_python_tooling(self) -> None:
        config = tomllib.loads((REPOSITORY_ROOT / "pyproject.toml").read_text())
        self.assertTrue((REPOSITORY_ROOT / "uv.lock").is_file())
        self.assertTrue(config["project"]["requires-python"])
        self.assertIs(config["tool"]["uv"]["package"], False)

    def test_skill_metadata_is_valid(self) -> None:
        skills = sorted((REPOSITORY_ROOT / "skills").glob("*/SKILL.md"))
        self.assertTrue(skills)
        for path in skills:
            with self.subTest(skill=path.parent.name):
                parts = path.read_text().split("---", 2)
                self.assertEqual(len(parts), 3)
                self.assertFalse(parts[0].strip())
                metadata = yaml.safe_load(parts[1])
                self.assertEqual(metadata["name"], path.parent.name)
                self.assertRegex(metadata["name"], r"\A[a-z0-9]+(?:-[a-z0-9]+)*\Z")
                self.assertIsInstance(metadata["description"], str)
                self.assertTrue(metadata["description"].strip())
                ui = yaml.safe_load((path.parent / "agents/openai.yaml").read_text())
                self.assertTrue(ui["interface"]["display_name"])
                self.assertIn("$" + metadata["name"], ui["interface"]["default_prompt"])
                self.assertNotIn("allow_implicit_invocation", ui["interface"])
                self.assertIsInstance(
                    ui.get("policy", {}).get("allow_implicit_invocation", True), bool
                )

    def test_skill_local_links_resolve_within_package(self) -> None:
        for skill in (REPOSITORY_ROOT / "skills").iterdir():
            if not skill.is_dir():
                continue
            for path in [skill / "SKILL.md", *skill.glob("references/**/*.md")]:
                targets = re.findall(r"\[[^]\n]*\]\(([^)\n]+)\)", path.read_text())
                for target in targets:
                    if re.match(r"[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(
                        "#"
                    ):
                        continue
                    destination = (path.parent / target.split("#", 1)[0]).resolve()
                    with self.subTest(file=str(path), target=target):
                        self.assertTrue(destination.is_relative_to(skill.resolve()))
                        self.assertTrue(destination.exists())

    def test_skill_text_is_portable(self) -> None:
        identities = (
            "/home/rheni", "/mnt/wsl/", "biohub", "rsna", "nemotron",
            "timeseries-det", "tailefcc",
        )
        text_suffixes = {".md", ".yaml", ".yml", ".py", ".toml", ".json", ".ts", ".tsx"}
        for path in (REPOSITORY_ROOT / "skills").rglob("*"):
            if path.is_file() and path.suffix in text_suffixes:
                body = path.read_text().lower()
                for identity in identities:
                    with self.subTest(file=str(path), identity=identity):
                        self.assertNotIn(identity, body)

    def test_starter_does_not_require_tailscale(self) -> None:
        for path in (SKILL_ROOT / "assets/viewer-starter").rglob("*"):
            if path.is_file():
                with self.subTest(file=str(path)):
                    self.assertNotIn("tailscale", path.read_text().lower())

    def test_repository_is_mit_licensed(self) -> None:
        body = (REPOSITORY_ROOT / "LICENSE").read_text()
        self.assertIn("MIT License", body)
        self.assertIn("Permission is hereby granted", body)

    def test_scaffold_copies_a_portable_starter_without_overwriting(self) -> None:
        script = SKILL_ROOT / "scripts" / "scaffold_viewer.py"
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "viewer"
            command = [
                sys.executable,
                str(script),
                str(target),
                "--project-name",
                "Example Viewer",
                "--package-name",
                "example_viewer",
            ]

            first = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertTrue((target / "backend" / "src" / "example_viewer" / "app.py").is_file())
            self.assertTrue((target / "frontend" / "src" / "App.tsx").is_file())
            rendered = "\n".join(
                path.read_text(encoding="utf-8")
                for path in target.rglob("*")
                if path.is_file()
            )
            self.assertNotIn("__VIEWER_PROJECT_NAME__", rendered)
            self.assertNotIn("__VIEWER_PACKAGE_NAME__", rendered)
            self.assertIn("Example Viewer", rendered)

            marker = target / "frontend" / "src" / "App.tsx"
            original = marker.read_text(encoding="utf-8")
            second = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(marker.read_text(encoding="utf-8"), original)
            self.assertRegex(second.stderr, re.compile(r"存在|exists", re.IGNORECASE))

    def test_report_contract_uses_the_compact_five_column_table(self) -> None:
        body = (
            SUMMARIZING_EXPERIMENTS_SKILL_ROOT / "references" / "report-contract.md"
        ).read_text(encoding="utf-8")

        lines = body.splitlines()
        header_index = next(
            (
                index
                for index, line in enumerate(lines)
                if [cell.strip() for cell in line.strip().strip("|").split("|")][
                    :2
                ]
                == ["実験", "親"]
            ),
            None,
        )
        self.assertIsNotNone(header_index, "標準の実験一覧表が必要です")
        assert header_index is not None

        header = [
            cell.strip()
            for cell in lines[header_index].strip().strip("|").split("|")
        ]
        self.assertEqual(len(header), 5)
        self.assertEqual(header[:4], ["実験", "親", "仮説", "結果"])
        self.assertTrue(header[4])
        self.assertNotIn(header[4], {"主指標", "主指標名", "<主指標名>"})

        separator = [
            cell.strip()
            for cell in lines[header_index + 1].strip().strip("|").split("|")
        ]
        self.assertEqual(len(separator), 5)
        self.assertTrue(
            all(re.fullmatch(r":?-{3,}:?", cell) for cell in separator),
            "標準表の区切り行が不正です",
        )

        example_rows: list[list[str]] = []
        for line in lines[header_index + 2 :]:
            if not line.strip().startswith("|"):
                break
            row = [cell.strip() for cell in line.strip().strip("|").split("|")]
            self.assertEqual(len(row), 5, f"標準表の行は5セル必要です: {line}")
            example_rows.append(row)

        self.assertTrue(example_rows, "標準表に実験例が必要です")
        result_status_pattern = re.compile(
            r"\A(?:支持|反証|判断保留|未評価)(?:\Z|[。:：\s])"
        )
        for experiment_id, parent_id, hypothesis, result, metric in example_rows:
            with self.subTest(experiment_id=experiment_id):
                self.assertRegex(experiment_id, r"\A\d+\Z")
                self.assertRegex(parent_id, r"\A(?:—|\d+(?:,\s*\d+)*)\Z")
                self.assertTrue(hypothesis, "仮説cellは空にできません")
                self.assertTrue(result, "結果cellは空にできません")
                self.assertRegex(
                    result,
                    result_status_pattern,
                    "結果cellは所定の判定から始める必要があります",
                )
                self.assertRegex(metric, r"\A(?:—|-?\d+(?:\.\d+)?)\Z")
                self.assertNotRegex(metric, r"(?:->|=>|→|←|Δ|delta|差分)")

        self.assertIsNone(
            result_status_pattern.match("支持されなかった"),
            "判定語の一部一致を受理してはいけません",
        )


if __name__ == "__main__":
    unittest.main()
