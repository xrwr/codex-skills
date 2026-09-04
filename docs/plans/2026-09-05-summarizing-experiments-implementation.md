# Summarizing Experiments Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 実験前の仮説記録を`managing-experiments`へ追加し、仮説と成果物を簡潔な5列表と個別サマリへ整理する`summarizing-experiments` skillを作る。

**Architecture:** `managing-experiments`は仮説、予想方向、判定指標を実験開始前にrepositoryの既存記録へ保存する。新しい`summarizing-experiments`は、`SKILL.md`に証拠確認workflowを、`references/report-contract.md`に5列表と個別サマリ形式を持ち、特定projectやML frameworkを必須化しない。

**Tech Stack:** Markdown、YAML、uv、Python 3.12 `unittest`、Codex subagent scenario tests

### Task 1: Managing Experiments の仮説記録をREDで定義する

**Files:**
- Create: `docs/plans/2026-09-05-summarizing-experiments-evaluation.md`
- Modify: `tests/test_skill_package.py`

1. 締切、既存config、過去結果への期待がある状況で、事前仮説を書かずに実験を投入しようとするscenarioを作る。
2. 現在の`managing-experiments`を提示したsubagentへscenarioを実行し、仮説をどこへ永続化するか曖昧な基準挙動を記録する。
3. `ManagingExperimentsSkillPackageTest`へ、実験開始前の仮説、予想する変化、判定指標の記録を要求するtestを追加する。
4. `uv run --locked python -m unittest -v tests.test_skill_package.ManagingExperimentsSkillPackageTest`を実行し、新しい契約が欠けてFAILすることを確認する。

### Task 2: Managing Experiments の仮説記録をGREENにする

**Files:**
- Modify: `skills/managing-experiments/SKILL.md`
- Modify: `docs/plans/2026-09-05-summarizing-experiments-evaluation.md`

1. 実験開始前に、検証可能な仮説、予想する変化、成否を判断する指標をrepository既存の実験記録へ保存する指示を追加する。
2. 既存規約がない場合は保存先を提案するだけに留め、任意のconfig schemaを強制しない。
3. package testを再実行しGREENを確認する。
4. 同じscenarioをスキルありで再実行し、事前記録が明示されることをevaluationへ記録する。

### Task 3: Summarizing Experiments の基準挙動をREDで記録する

**Files:**
- Modify: `docs/plans/2026-09-05-summarizing-experiments-evaluation.md`

1. 次の4 scenarioを作る。
   - 結果だけがあり、事前仮説がない。
   - queue完了とcheckpointはあるが、最終評価artifactがない。
   - 多数のmetadataを一つの横長表へ入れたくなる。
   - LLMのteacher traceを含む元スキルを、画像分類実験へそのまま適用したくなる。
2. 新スキルを提示せずsubagentへ実行し、仮説の後付け、状態混同、表の肥大化、domain固有化を逐語的に記録する。
3. 防ぐべき失敗と、一般的なagent能力へ任せる事項を分ける。

### Task 4: Summarizing Experiments package契約をREDにする

**Files:**
- Modify: `tests/test_skill_package.py`

1. `SUMMARIZING_EXPERIMENTS_SKILL_ROOT`と`SummarizingExperimentsSkillPackageTest`を追加する。
2. frontmatterが`name`と`description`だけで、descriptionが`Use when `から始まることを検査する。
3. packageが`SKILL.md`、`agents/openai.yaml`、`references/report-contract.md`だけを含むことを検査する。
4. 個人名、絶対path、competition名、SFT、teacher、trace、固定frameworkを含まないことを検査する。
5. 5列が`実験`、`親`、`仮説`、`結果`、動的な主指標であり、指標セルへ矢印や差分を詰めないことを検査する。
6. `uv run --locked python -m unittest -v tests.test_skill_package.SummarizingExperimentsSkillPackageTest`を実行し、skill directory不在でFAILすることを確認する。

### Task 5: Summarizing Experiments packageをGREENにする

**Files:**
- Create: `skills/summarizing-experiments/SKILL.md`
- Create: `skills/summarizing-experiments/agents/openai.yaml`
- Create: `skills/summarizing-experiments/references/report-contract.md`

1. `init_skill.py summarizing-experiments --path skills --resources references`を、確定したinterface値付きで実行する。
2. REDで観測した失敗だけに対応する最小の`SKILL.md`を書く。
3. `report-contract.md`へ全体サマリ、5列表、動的な指標見出し、個別サマリ、証拠と状態の契約を書く。
4. 一つの画像分類実験例で、短いID、親ID、仮説、結果、絶対F1を示す。
5. package testを再実行しGREENを確認する。

### Task 6: Pressure GREEN とREFACTOR

**Files:**
- Modify: `skills/summarizing-experiments/SKILL.md`
- Modify: `skills/summarizing-experiments/references/report-contract.md`
- Modify: `docs/plans/2026-09-05-summarizing-experiments-evaluation.md`

1. Task 3と同じscenarioへ新スキルを提示してsubagentを再実行する。
2. 仮説後付け、成果物なしの結果断定、表の肥大化、domain固有化が消えたか比較する。
3. 新しい抜け道または合理化を逐語的に記録し、必要な箇所だけ修正する。
4. scenarioを再実行し、5列表と証拠契約を再確認する。

### Task 7: Distribution と最終検証

**Files:**
- Modify: `README.md`

1. Skills一覧、install例、Developmentのvalidator対象へ`summarizing-experiments`を追加する。
2. `uv run --locked python -m unittest -v tests/test_skill_package.py`を実行する。
3. `uv run --locked python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/managing-experiments`を実行する。
4. `uv run --locked python ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py skills/summarizing-experiments`を実行する。
5. `rg`で個人・project識別子、placeholder、不要なdomain固有語がないことを確認する。
6. `git diff --check`とbranch全体のdiffを確認する。
7. 変更をレビューし、現在のmain worktreeにある無関係な未コミット変更と分離した状態で引き渡す。
