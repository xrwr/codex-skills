---
name: building-data-science-projects
description: Use when a user asks to create, scaffold, or restructure a Python data-science or machine-learning project, choose its libraries or tooling stack, or establish project-wide conventions for dependencies, notebooks, typing, and directories, including 「データサイエンスプロジェクト」「おすすめライブラリ」「ライブラリ選定」「プロジェクト構成」.
---

# Building Data Science Projects

## Overview

既存repositoryの契約を優先し、greenfieldまたは明示的な再構成でだけ、必要最小限のPython data-science stackとproject structureを選ぶ。推奨一覧を一括導入せず、実際のtask、data、runtime、運用境界から依存を決める。

## Workflow

1. `pyproject.toml`、lockfile、import、config、scripts、tests、CIを検査し、greenfieldか既存projectかを判定する。
2. 既存projectでは現在のpackage manager、framework、directory contractを維持する。移行は明示的に依頼された範囲だけ行う。
3. Library選定では[Python stack](references/python-stack.md)を読み、現在必要なcategoryだけを追加する。
4. 新規作成または構造変更では[project structure](references/project-structure.md)を読み、ownerのないdirectoryや将来用placeholderを作らない。
5. Dependency declaration、lockfile、import、対象testまたは最小entrypointを検証する。導入しただけで利用可能と判断しない。

Experiment config、run、artifact evidenceを扱う場合は、内容を重複させず`managing-experiments`を使う。Viewerを作る場合は`building-viewers`を使う。

## Quick Reference

| 依頼 | 読む参照 | 基本判断 |
|---|---|---|
| 新規Python ML project | 両方 | 最小stackとownerのあるdirectoryだけ作る |
| Library・tool選定 | `python-stack.md` | taskに必要なcategoryだけ選ぶ |
| Repository再構成 | `project-structure.md` | 現行contractを確認してから境界を変える |
| 既存projectで通常作業 | 原則不要 | 既存stackをそのまま使う |

## Common Mistakes

- 推奨一覧を全部installする: 今回のentrypointがimportするdependencyだけを追加する。
- Greenfield向けdefaultを既存repositoryへ強制する: 現在のlockfileと実装を正本にする。
- Versionをskillへ固定する: projectのdependency declarationとlockfileへ記録する。
- Hydra、Lightning、W&Bを常に導入する: complexityまたは運用上のconsumerがある場合だけ選ぶ。
- Data-science projectを名乗るだけで空directoryを量産する: 現在のownerとartifact contractがあるものだけ作る。

## Red Flags

- Userの依頼なしにpackage managerやframeworkを移行する
- 同じ用途のlibraryを比較せず複数追加する
- `src`のdomain codeへconfig framework固有objectを渡す
- Generated data、credential、run outputをsource treeへ混在させる
