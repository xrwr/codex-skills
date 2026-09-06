---
name: managing-experiments
description: Use when a repository task explicitly concerns an experiment or run, including creating experiment configs, planning an ablation or baseline, changing experimental configuration, reproducing an experiment, retrying or restarting a run, or checking experiment status or results.
---

# Managing Experiments

## Overview

実験設定を自己完結させ、runの状態を現在のattemptに帰属する成果物で判定する。既存repositoryの契約を正本とし、一般的なDataset実装などexperiment config・run・結果管理を扱わない依頼には適用しない。

## Workflow

1. Repository、config、scripts、tests、output、log、job stateを先に検査する。実在する契約と不明点を分ける。
2. 新規または変更した実験を開始する場合は、実験開始前に、検証可能な仮説、比較対象、予想する変化、成否を判断する指標とその期待方向または閾値をrepository既存の実験記録へ保存する。指標名だけを判定条件にしない。
3. 既存規約がなければ保存先を提案してユーザーと合意し、実際の保存が完了するまで実験を開始しない。任意のconfig schemaや特定pathを強制しない。
4. 過去runのstatus/result確認で事前仮説がなければ、欠落として報告し、結果から仮説を後付けしない。
5. 入力、split、意味上の変更、必要成果物を特定する。
6. Config作成・変更では[config architecture](references/config-architecture.md)を読む。experiment configを自己完結したselection manifestにする。
7. 実行、retry/restart、status/result確認、複数GPUへの割当では[run lifecycle](references/run-lifecycle.md)を読む。experimentとattemptを分離し、資源割当と成果物のprovenanceを検証する。
8. 実験投入時は、[run lifecycle](references/run-lifecycle.md)に従って終了後の要約jobも登録する。補助記録は本実験のoutputツリーの外へ置く。
9. 変更範囲、確認済み証拠、未解決事項を報告する。依頼のないstart、stop、delete、submitを行わない。

Hydra、pueue、W&B、Lightningなどはrepositoryに既存し、現在利用可能な場合だけ使う。導入や必須化を推測しない。

## Quick Reference

| 依頼 | 必ず確認するもの | 読む参照 |
|---|---|---|
| Experiment config・ablation・baseline | 仮説、比較対象、判定条件、保存先、defaults、component所有者、resolved config | `config-architecture.md` |
| 実行・retry/restart | experiment ID、attempt ID、旧output、実行記録 | `run-lifecycle.md` |
| 投入後の自動要約 | 最終評価job、対象attempt、成果物、要約保存先、Codex認証、後続job ID | `run-lifecycle.md` |
| 複数GPUでの実行 | Pueue group、割当GPU、device binding、attempt | `run-lifecycle.md` |
| Status・result | 必要成果物、current attemptへのprovenance | `run-lifecycle.md` |
