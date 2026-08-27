# Managing Experiments Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 設定所有権、実験系譜、成果物に基づくrun状態を扱う、配布可能な`managing-experiments` skillを作る。

**Architecture:** `SKILL.md`は発火条件と最小workflowだけを保持し、設定境界を`config-architecture.md`、runの状態・再試行を`run-lifecycle.md`へ分離する。scriptとassetは作らず、対象repositoryに存在するtoolだけを利用する。

**Tech Stack:** Markdown、YAML、uv、Python 3.12 `unittest`、Codex subagent pressure tests

### Task 1: Skill behavior baseline

**Files:**
- Create: `docs/plans/2026-08-28-managing-experiments-evaluation.md`

1. 設定複製、未完了artifact、OOM再試行、negative triggerの4 scenarioを作る。
2. `managing-experiments`を提示せず、独立したsubagentへscenarioを実行させる。
3. 各agentの選択、状態表現、合理化を原文のままevaluation文書へ記録する。
4. skillが防ぐべき非自明な失敗だけを一覧化する。
5. evaluation文書だけをcommitする。

### Task 2: uv-managed repository tooling

**Files:**
- Create: `pyproject.toml`
- Create: `uv.lock`
- Modify: `tests/test_skill_package.py`
- Modify: `.github/workflows/validate.yml`
- Modify: `README.md`

1. repository tooling testへ、uv project metadata、lockfile、CIのuv setup、READMEの`uv run` commandを検査するtestを追加する。
2. `uv run python -m unittest -v tests.test_skill_package.RepositoryToolingTest`を実行し、metadata未実装を理由にFAILすることを確認する。
3. package化しない最小の`pyproject.toml`を作り、`uv lock`でlockfileを生成する。
4. CIへuvをsetupし、package testを`uv run python -m unittest`で実行する。
5. READMEのPython development commandを`uv run`へ統一する。
6. repository tooling testと既存testをGREENにし、uv setupをcommitする。

### Task 3: Package contract RED

**Files:**
- Modify: `tests/test_skill_package.py`

1. `ManagingExperimentsSkillPackageTest`を追加し、次を検査する。
   - frontmatterは`name`と`description`だけで、descriptionは`Use when `から始まる。
   - `SKILL.md`、`agents/openai.yaml`、2 referencesだけが必須resourceである。
   - `controlled-comparisons.md`、`scripts/`、`assets/`がない。
   - 個人名、絶対path、既知のproject名、特定toolの必須表現がない。
   - gradient accumulation、effective batch、一般的な比較論がない。
   - config ownership、experiment非継承、artifact evidence、partial/verified、retry lineageを含む。
2. `uv run python -m unittest -v tests.test_skill_package.ManagingExperimentsSkillPackageTest`を実行する。
3. skill directoryが存在しないことを理由にFAILすることを確認する。
4. testだけをcommitする。

### Task 4: Skill package GREEN

**Files:**
- Create: `skills/managing-experiments/SKILL.md`
- Create: `skills/managing-experiments/agents/openai.yaml`
- Create: `skills/managing-experiments/references/config-architecture.md`
- Create: `skills/managing-experiments/references/run-lifecycle.md`

1. `skill-creator/references/openai_yaml.md`を最後まで読む。
2. `init_skill.py managing-experiments --path skills --resources references`を、確定した3つのinterface値付きで実行する。
3. REDで観測した失敗だけに対応する最小の`SKILL.md`とreferencesを書く。
4. experiment config間の継承禁止、共有componentの抽出条件、実装のないgroupを作らない条件を記述する。
5. job、process、checkpoint、metric、final artifactを区別し、`queued/running/failed/partial/verified/unknown`を証拠に結び付ける。
6. 同一仮説のretryではIDを維持し、既存出力を退役させて混在を防ぐ具体例を一つだけ記述する。
7. package testを再実行しGREENを確認する。
8. skill packageをcommitする。

### Task 5: Skill pressure GREEN and REFACTOR

**Files:**
- Modify: `skills/managing-experiments/SKILL.md`
- Modify: `skills/managing-experiments/references/config-architecture.md`
- Modify: `skills/managing-experiments/references/run-lifecycle.md`
- Modify: `docs/plans/2026-08-28-managing-experiments-evaluation.md`

1. Task 1と同じscenarioへskill全文と必要なreferenceを提示してsubagentを再実行する。
2. 同じfailureが消えたかを比較し、新しい合理化を原文で記録する。
3. 新しい抜け道があれば、該当箇所だけを明示的に閉じる。
4. 同じscenarioを再実行し、negative triggerを含めて再検証する。
5. evaluationとrefactorをcommitする。

### Task 6: Distribution and verification

**Files:**
- Modify: `README.md`

1. Skills一覧とinstall例へ`managing-experiments`を追加する。
2. `uv run python -m unittest discover -s tests -v`を実行し、全testがPASSすることを確認する。
3. `uv run python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/managing-experiments`を実行する。
4. 一時`CODEX_HOME`へGitHub path相当のskill directoryをcopyし、必須4ファイルだけで利用できることを確認する。
5. `rg`で個人情報、project識別子、一般論、placeholderの残存がないことを確認する。
6. `git diff --check`とbranch全体のdiffを確認する。
7. review後に最終commitを作り、`origin/main`へ統合してpushする。
