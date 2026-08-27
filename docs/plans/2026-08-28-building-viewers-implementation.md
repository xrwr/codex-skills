# Building Viewers Skill Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 配布可能な`building-viewers` skillと、React＋TypeScript＋FastAPIの読み取り専用starterを作る。

**Architecture:** Skill本文は判断workflowだけを保持し、詳細契約と配信判断をreferencesへ分離する。新規構築用コードはassetへ置き、安全なscaffold scriptで対象directoryへ展開する。

**Tech Stack:** Markdown、Python 3.12、FastAPI、Pydantic、React 19、TypeScript、Vite、Vitest、Testing Library

### Task 1: Package contract

**Files:**
- Test: `tests/test_skill_package.py`

1. 必須metadata、resource、portable path、MIT、scaffold非破壊性のtestを書く。
2. `python3 -m unittest discover -s tests -v`を実行する。
3. skill未実装を理由に全testがFAILすることを確認する。

### Task 2: Skill workflowとreferences

**Files:**
- Create: `skills/building-viewers/SKILL.md`
- Create: `skills/building-viewers/references/contracts.md`
- Create: `skills/building-viewers/references/deployment.md`
- Create: `skills/building-viewers/agents/openai.yaml`

1. genericなViewer発火条件をfrontmatter testで固定する。
2. REDシナリオで不足したURL/mobile契約と、過剰だった配信標準化をworkflowへ反映する。
3. contractとdeploymentの詳細をreferencesへ分離する。
4. package testのmetadata関連をGREENにする。

### Task 3: Safe scaffold

**Files:**
- Create: `skills/building-viewers/scripts/scaffold_viewer.py`
- Test: `tests/test_skill_package.py`

1. 存在するtargetを拒否するtestを確認する。
2. asset copy、path token rename、text token置換を実装する。
3. `python3 -m unittest discover -s tests -v`でGREENを確認する。

### Task 4: FastAPI starter

**Files:**
- Create: `skills/building-viewers/assets/viewer-starter/backend/pyproject.toml`
- Create: `skills/building-viewers/assets/viewer-starter/backend/src/__VIEWER_PACKAGE_NAME__/*.py`
- Create: `skills/building-viewers/assets/viewer-starter/backend/tests/*.py`

1. summary/detail/issues/health APIのcontract testを書く。
2. 個別issue隔離とopaque IDを持つJSON catalogを実装する。
3. `uv run --project ... pytest`でGREENを確認する。

### Task 5: React starter

**Files:**
- Create: `skills/building-viewers/assets/viewer-starter/frontend/package.json`
- Create: `skills/building-viewers/assets/viewer-starter/frontend/src/*`
- Create: `skills/building-viewers/assets/viewer-starter/frontend/src/*.test.tsx`

1. 一覧→詳細、URL復元、loading/empty/error、mobile shellのtestを書く。
2. 最小componentとCSSを実装する。
3. `npm test`、`npm run lint`、`npm run build`でGREENを確認する。

### Task 6: Distribution and verification

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `.github/workflows/validate.yml`

1. GitHub path install、release tag、dotfilesとの分離をrepository READMEへ書く。
2. MIT LicenseとCIを追加する。
3. skill validator、package test、scaffold smoke、backend、frontendを全実行する。
4. skillありの同一シナリオを再実行し、過不足をrefactorする。
5. commit後、GitHub認証を確認して公開repositoryへpushする。
