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
MANAGING_EXPERIMENTS_SKILL_ROOT = REPOSITORY_ROOT / "skills" / "managing-experiments"
MODEL_DIAGRAM_SKILL_ROOT = (
    REPOSITORY_ROOT / "skills" / "drawing-model-architecture-diagrams"
)


class RepositoryToolingTest(unittest.TestCase):
    """リポジトリ自身のPython検証環境がuv管理であることを検証する。"""

    def test_repository_is_a_uv_managed_non_package_project(self) -> None:
        pyproject_file = REPOSITORY_ROOT / "pyproject.toml"
        lock_file = REPOSITORY_ROOT / "uv.lock"

        self.assertTrue(pyproject_file.is_file(), "pyproject.tomlが必要です")
        self.assertTrue(lock_file.is_file(), "uv.lockが必要です")

        config = tomllib.loads(pyproject_file.read_text(encoding="utf-8"))
        project = config["project"]
        self.assertEqual(project["name"], "codex-skills")
        self.assertEqual(project["version"], "0.0.0")
        self.assertEqual(project["requires-python"], ">=3.12")
        self.assertEqual(project["dependencies"], [])
        self.assertIs(config["tool"]["uv"]["package"], False)
        self.assertNotIn("build-system", config)

    def test_package_ci_uses_uv_with_the_locked_lockfile(self) -> None:
        workflow = (REPOSITORY_ROOT / ".github" / "workflows" / "validate.yml").read_text(
            encoding="utf-8"
        )
        package_job = workflow.split("  package:", maxsplit=1)[1].split(
            "  starter:", maxsplit=1
        )[0]

        self.assertRegex(
            package_job,
            re.compile(
                r"^      - uses: astral-sh/setup-uv@"
                r"c771a70e6277c0a99b617c7a806ffedaca235ff9 # v9\.0\.0$",
                re.MULTILINE,
            ),
        )
        self.assertRegex(
            package_job,
            re.compile(
                r"^      - run: uv run --locked python -m unittest -v "
                r"tests/test_skill_package\.py$",
                re.MULTILINE,
            ),
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


class ManagingExperimentsSkillPackageTest(unittest.TestCase):
    """配布可能な実験管理skillの最小package契約を検証する。"""

    def test_metadata_uses_generic_experiment_triggers(self) -> None:
        self.assertTrue(
            MANAGING_EXPERIMENTS_SKILL_ROOT.is_dir(),
            "managing-experiments skill directoryが必要です",
        )
        skill_file = MANAGING_EXPERIMENTS_SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "SKILL.mdが必要です")
        body = skill_file.read_text(encoding="utf-8")
        frontmatter_match = re.match(
            r"\A---\n(?P<frontmatter>.*?)\n---(?:\n|\Z)", body, re.DOTALL
        )

        self.assertIsNotNone(frontmatter_match, "YAML frontmatterが必要です")
        assert frontmatter_match is not None
        frontmatter = frontmatter_match.group("frontmatter").splitlines()
        self.assertEqual(len(frontmatter), 2)
        self.assertEqual(frontmatter[0], "name: managing-experiments")
        self.assertTrue(frontmatter[1].startswith("description: "))

        description = frontmatter[1].removeprefix("description: ")
        self.assertTrue(description.startswith("Use when "))
        lowered_description = description.lower()
        self.assertIn("experiment", lowered_description)
        self.assertIn("run", lowered_description)

    def test_package_contains_exact_distribution_resources(self) -> None:
        self.assertTrue(
            MANAGING_EXPERIMENTS_SKILL_ROOT.is_dir(),
            "managing-experiments skill directoryが必要です",
        )
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/config-architecture.md",
            "references/run-lifecycle.md",
        }
        actual = {
            path.relative_to(MANAGING_EXPERIMENTS_SKILL_ROOT).as_posix()
            for path in MANAGING_EXPERIMENTS_SKILL_ROOT.rglob("*")
            if path.is_file()
        }

        self.assertEqual(actual, expected)
        self.assertFalse(
            (MANAGING_EXPERIMENTS_SKILL_ROOT / "controlled-comparisons.md").exists()
        )
        self.assertFalse((MANAGING_EXPERIMENTS_SKILL_ROOT / "scripts").exists())
        self.assertFalse((MANAGING_EXPERIMENTS_SKILL_ROOT / "assets").exists())
        self.assertFalse((MANAGING_EXPERIMENTS_SKILL_ROOT / "README.md").exists())

    def test_package_is_portable_and_excludes_user_requested_topics(self) -> None:
        self.assertTrue(
            MANAGING_EXPERIMENTS_SKILL_ROOT.is_dir(),
            "managing-experiments skill directoryが必要です",
        )
        text_files = [
            path
            for path in MANAGING_EXPERIMENTS_SKILL_ROOT.rglob("*")
            if path.is_file()
            and path.suffix.lower() in {".md", ".txt", ".yaml", ".yml"}
        ]
        self.assertTrue(text_files, "skillのtext fileが必要です")
        forbidden_identities = (
            "/home/",
            "rheni",
            "rsna",
            "biohub",
            "timeseries-det",
            "tailefcc",
        )
        forbidden_topics = (
            "controlled-comparisons",
            "gradient accumulation",
            "accumulate_grad_batches",
            "effective batch",
            "勾配蓄積",
        )

        for path in text_files:
            text = path.read_text(encoding="utf-8")
            lowered = text.lower()
            for token in forbidden_identities:
                with self.subTest(path=path, identity=token):
                    self.assertNotIn(token, lowered)
            for token in forbidden_topics:
                with self.subTest(path=path, topic=token):
                    self.assertNotIn(token, lowered)

    def test_openai_metadata_supports_implicit_invocation(self) -> None:
        self.assertTrue(
            MANAGING_EXPERIMENTS_SKILL_ROOT.is_dir(),
            "managing-experiments skill directoryが必要です",
        )
        metadata_file = MANAGING_EXPERIMENTS_SKILL_ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata_file.is_file(), "agents/openai.yamlが必要です")
        body = metadata_file.read_text(encoding="utf-8")

        self.assertIn('display_name: "Experiment Manager"', body)
        self.assertRegex(body, r'default_prompt: ".*\$managing-experiments.*"')
        self.assertIn("allow_implicit_invocation: true", body)

    def test_run_lifecycle_defines_multi_gpu_resource_contract(self) -> None:
        """複数GPUではPueue独立jobを既定にし、DDPを暗黙に使わない。"""

        lifecycle_file = (
            MANAGING_EXPERIMENTS_SKILL_ROOT / "references" / "run-lifecycle.md"
        )
        body = lifecycle_file.read_text(encoding="utf-8")

        self.assertIn("## GPU Resource Contract", body)
        self.assertIn("Pueueを既定", body)
        self.assertIn("独立した1-GPU job", body)
        self.assertIn("parallel=1", body)
        self.assertIn("CUDA_VISIBLE_DEVICES", body)
        self.assertIn("相互排他", body)
        self.assertIn("DDP", body)
        self.assertRegex(body, r"明示.*指示.*DDP")
        self.assertNotIn("sbatch --gres", body)


class ModelArchitectureDiagramSkillPackageTest(unittest.TestCase):
    """モデルアーキテクチャ図skillの配布契約を検証する。"""

    def test_metadata_targets_model_architecture_diagrams(self) -> None:
        skill_file = MODEL_DIAGRAM_SKILL_ROOT / "SKILL.md"
        self.assertTrue(skill_file.is_file(), "SKILL.mdが必要です")
        body = skill_file.read_text(encoding="utf-8")
        frontmatter_match = re.match(
            r"\A---\n(?P<frontmatter>.*?)\n---(?:\n|\Z)", body, re.DOTALL
        )

        self.assertIsNotNone(frontmatter_match, "YAML frontmatterが必要です")
        assert frontmatter_match is not None
        frontmatter = frontmatter_match.group("frontmatter").splitlines()
        self.assertEqual(len(frontmatter), 2)
        self.assertEqual(frontmatter[0], "name: drawing-model-architecture-diagrams")
        description = frontmatter[1].removeprefix("description: ")
        self.assertTrue(description.startswith("Use when "))
        self.assertIn("explicitly asks", description)
        self.assertIn("architecture", description.lower())
        self.assertIn("SVG", description)
        self.assertIn("図", description)

    def test_package_stays_minimal_without_renderer_or_diagram_dsl(self) -> None:
        expected = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/svg-guidelines.md",
        }
        actual = {
            path.relative_to(MODEL_DIAGRAM_SKILL_ROOT).as_posix()
            for path in MODEL_DIAGRAM_SKILL_ROOT.rglob("*")
            if path.is_file()
        }

        self.assertEqual(actual, expected)
        self.assertFalse((MODEL_DIAGRAM_SKILL_ROOT / "scripts").exists())
        self.assertFalse((MODEL_DIAGRAM_SKILL_ROOT / "assets").exists())

    def test_skill_defines_shape_and_semantic_granularity_contracts(self) -> None:
        body = (MODEL_DIAGRAM_SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("入力shapeと出力shapeは必須", body)
        self.assertIn("責務", body)
        self.assertIn("総要素数を上限で縛らない", body)
        self.assertIn("視覚文法", body)
        self.assertIn("一つの抽象度", body)
        self.assertIn("一箇所だけ", body)
        self.assertIn("省略記号", body)
        self.assertIn("branch", body)
        self.assertIn("merge", body)
        self.assertIn("shared weight", body)
        self.assertIn("symbolic shape", body)
        self.assertIn("shape unknown", body)
        self.assertIn("中間tensor", body)
        self.assertIn("最終入力と最終出力", body)
        self.assertIn("実データ", body)
        self.assertIn("operation blockには処理名だけ", body)
        self.assertIn("shapeはblockの外", body)
        self.assertIn("補足説明を置かない", body)
        self.assertIn("axis continuity", body)
        self.assertIn("推測", body)
        self.assertIn("SVGを直接", body)
        self.assertIn("実際にrender", body)
        self.assertRegex(body, r"U-Net Encoder.*一つ")

    def test_skill_requires_a_visible_shape_for_every_external_input_and_output(self) -> None:
        skill_body = (MODEL_DIAGRAM_SKILL_ROOT / "SKILL.md").read_text(
            encoding="utf-8"
        )
        reference_body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "各最終入力と各最終出力",
            "必ず個別に表示",
            "不明でも省略せず",
            "shape unknown",
        ):
            with self.subTest(token=token):
                self.assertIn(token, skill_body)

        for token in (
            "対応するglyphに隣接",
            "複数の入出力",
            "縮小表示でも",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference_body)

    def test_svg_reference_defines_visual_grammar_and_tensor_glyphs(self) -> None:
        body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "outer panel",
            "実データに近いglyph",
            "sequence",
            "feature map",
            "vector",
            "matrix",
            "rank",
            "TeX",
            "数式だけ",
            "交差を0",
            "凡例",
        ):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_svg_reference_makes_merges_and_repeated_feedback_explicit(self) -> None:
        body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "複数tensorから一つの出力",
            "演算glyph",
            "branch point",
            "反復範囲",
            "一回の反復内",
            "中間tensor",
        ):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_svg_reference_distinguishes_shared_operations_and_persistent_state(self) -> None:
        body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "独立したport",
            "shared-weight marker",
            "永続artifact",
            "build/index",
            "inference lane",
            "永続artifactだけ",
        ):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_svg_reference_defines_compact_arrow_geometry(self) -> None:
        body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "block outlineの0.6倍",
            "stroke幅の3〜4倍",
            "target glyphの高さの1/3",
            "target境界に垂直",
            "arrowhead長の2倍",
            "marker tip",
        ):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_svg_reference_preserves_editability_and_accessibility(self) -> None:
        body = (
            MODEL_DIAGRAM_SKILL_ROOT / "references" / "svg-guidelines.md"
        ).read_text(encoding="utf-8")

        for token in (
            "viewBox",
            "<text>",
            "marker-end",
            "<title>",
            "<desc>",
            "外部font",
            "文字切れ",
            "矢印",
        ):
            with self.subTest(token=token):
                self.assertIn(token, body)

    def test_openai_metadata_supports_implicit_invocation(self) -> None:
        metadata_file = MODEL_DIAGRAM_SKILL_ROOT / "agents" / "openai.yaml"
        self.assertTrue(metadata_file.is_file(), "agents/openai.yamlが必要です")
        body = metadata_file.read_text(encoding="utf-8")

        self.assertIn('display_name: "Model Architecture Diagrammer"', body)
        self.assertRegex(
            body,
            r'default_prompt: ".*\$drawing-model-architecture-diagrams.*"',
        )
        self.assertIn("allow_implicit_invocation: true", body)

    def test_readme_lists_the_new_skill_and_install_path(self) -> None:
        readme = (REPOSITORY_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("### `drawing-model-architecture-diagrams`", readme)
        self.assertIn("--path skills/drawing-model-architecture-diagrams", readme)


if __name__ == "__main__":
    unittest.main()
