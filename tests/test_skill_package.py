from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = REPOSITORY_ROOT / "skills" / "building-viewers"


class RepositoryToolingTest(unittest.TestCase):
    """リポジトリ自身のPython検証環境がuv管理であることを検証する。"""

    def test_repository_is_a_uv_managed_non_package_project(self) -> None:
        pyproject_file = REPOSITORY_ROOT / "pyproject.toml"
        lock_file = REPOSITORY_ROOT / "uv.lock"

        self.assertTrue(pyproject_file.is_file(), "pyproject.tomlが必要です")
        self.assertTrue(lock_file.is_file(), "uv.lockが必要です")

        config = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
        self.assertEqual(
            config["project"],
            {
                "name": "codex-skills",
                "version": "0.0.0",
                "requires-python": ">=3.12",
                "dependencies": [],
            },
        )
        self.assertEqual(config["tool"]["uv"], {"package": False})
        self.assertNotIn("build-system", config)

    def test_package_ci_uses_uv_with_the_frozen_lockfile(self) -> None:
        workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        package_job = workflow.split("  package:", maxsplit=1)[1].split(
            "  starter:", maxsplit=1
        )[0]

        self.assertIn(
            "astral-sh/setup-uv@c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9.0.0",
            package_job,
        )
        self.assertIn(
            "uv run --frozen python -m unittest -v tests/test_skill_package.py",
            package_job,
        )

    def test_development_commands_run_python_through_uv(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")
        development = readme.split("## Development", maxsplit=1)[1].split(
            "## License", maxsplit=1
        )[0]

        self.assertIn(
            "uv run python -m unittest -v tests/test_skill_package.py", development
        )
        self.assertIn(
            "uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py",
            development,
        )


class SkillPackageTest(unittest.TestCase):
    """配布可能なViewer skillのpackage契約を検証する。"""

    def test_skill_metadata_uses_generic_viewer_triggers(self) -> None:
        skill_file = SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "SKILL.mdが必要です")
        body = skill_file.read_text(encoding="utf-8")
        frontmatter = body.split("---", maxsplit=2)[1].strip().splitlines()

        self.assertEqual(frontmatter[0], "name: building-viewers")
        self.assertEqual(len(frontmatter), 2)
        description = frontmatter[1].removeprefix("description: ")
        self.assertTrue(description.startswith("Use when "))
        self.assertIn("viewer", description.lower())
        self.assertIn("ビューア", description)

    def test_skill_has_only_distribution_resources(self) -> None:
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/contracts.md",
            "references/deployment.md",
            "assets/viewer-starter/backend/pyproject.toml",
            "assets/viewer-starter/frontend/package.json",
            "scripts/scaffold_viewer.py",
        }

        for relative_path in expected:
            self.assertTrue((SKILL_ROOT / relative_path).is_file(), relative_path)
        self.assertFalse((SKILL_ROOT / "README.md").exists())

    def test_skill_is_free_of_machine_and_project_identity(self) -> None:
        self.assertTrue(SKILL_ROOT.is_dir(), "skill directoryが必要です")
        forbidden = (
            "/home/",
            "rheni",
            "rsna",
            "biohub",
            "timeseries-det",
            "tailefcc",
        )

        for path in SKILL_ROOT.rglob("*"):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or path.suffix in {".png", ".jpg", ".woff2", ".pyc"}
            ):
                continue
            text = path.read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text.lower(), f"{path}: {token}")

    def test_tailscale_is_optional_and_not_baked_into_starter(self) -> None:
        deployment_file = SKILL_ROOT / "references" / "deployment.md"
        self.assertTrue(deployment_file.is_file(), "deployment referenceが必要です")
        deployment = deployment_file.read_text(encoding="utf-8")
        self.assertRegex(deployment, r"Tailscale.*任意|任意.*Tailscale")
        self.assertIn("利用可能", deployment)

        starter_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (SKILL_ROOT / "assets" / "viewer-starter").rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
        self.assertNotIn("tailscale", starter_text.lower())

    def test_openai_metadata_supports_implicit_invocation(self) -> None:
        metadata_file = SKILL_ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata_file.is_file(), "agents/openai.yamlが必要です")
        body = metadata_file.read_text(encoding="utf-8")

        self.assertIn('display_name: "Viewer Builder"', body)
        self.assertRegex(body, r'default_prompt: ".*\$building-viewers.*"')
        self.assertIn("allow_implicit_invocation: true", body)

    def test_repository_is_mit_licensed(self) -> None:
        license_file = REPOSITORY_ROOT / "LICENSE"
        self.assertTrue(license_file.is_file(), "MIT LICENSEが必要です")
        license_text = license_file.read_text(encoding="utf-8")

        self.assertIn("MIT License", license_text)
        self.assertIn("Permission is hereby granted", license_text)

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


if __name__ == "__main__":
    unittest.main()
