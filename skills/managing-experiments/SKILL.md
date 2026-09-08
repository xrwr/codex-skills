---
name: managing-experiments
description: Use when a repository task explicitly concerns an experiment or run, including creating experiment configs, planning an ablation or baseline, changing experimental configuration, reproducing an experiment, retrying or restarting a run, or checking experiment status or results.
---

# Managing Experiments

## Overview

Experimentを仮説と検証計画の単位、trialを計画内の条件、attemptを実行履歴として管理する。実験設定を自己完結させ、状態を対象attemptの成果物で判定する。既存repositoryの契約を正本とし、実験管理を扱わない一般的な実装には適用しない。

## Workflow

1. Repository、config、scripts、tests、output、log、job stateを先に検査する。実在する契約と不明点を分ける。
2. 採番・計画時は[run lifecycle](references/run-lifecycle.md)のIdentityを読み、過去のexperimentも探して、trial追加・retry・新experimentを判別する。開始前に実験全体の仮説と根拠、比較対象、固定条件、変更軸・探索範囲、予算、評価方法と期待方向または閾値を既存の実験記録へ保存する。各trialには仮説の何を確かめる条件かを残す。明示的な探索は同参照の規則に従う。
3. 既存規約がなければ保存先を提案してユーザーと合意し、実際の保存が完了するまで実験を開始しない。任意のconfig schemaや特定pathを強制しない。
4. 過去runのstatus/result確認で事前仮説がなければ、記録済みの仮説生成の探索と記録の欠落を区別し、結果から事前仮説を後付けしない。
5. 入力、split、意味上の変更、必要成果物を特定する。
6. Config作成・変更では[config architecture](references/config-architecture.md)を読む。experiment configを自己完結したselection manifestにする。
7. 実行、retry/restart、status/result確認、W&B、複数GPUへの割当では[run lifecycle](references/run-lifecycle.md)を読む。experiment・trial・fold・attemptを照合し、資源割当と成果物のprovenanceを検証する。
8. 投入時は同参照に従って、単独検証または上限を定めた探索バッチの評価後に要約jobを登録する。補助記録は本実験のoutputツリーの外へ置く。
9. 変更範囲、確認済み証拠、未解決事項を報告する。依頼のないstart、stop、delete、submitを行わない。

Hydra、pueue、W&B、Lightningなどはrepositoryに既存し、現在利用可能な場合だけ使う。導入や必須化を推測しない。

## Quick Reference

| 依頼 | 必ず確認するもの | 読む参照 |
|---|---|---|
| 採番・過去実験への追加・探索計画 | 実験全体の仮説、固定条件、変更軸、予算、基準trial | `run-lifecycle.md` のIdentity |
| Experiment/trial config・ablation・baseline | 比較対象、判定条件、保存先、defaults、component所有者、resolved config | `config-architecture.md` |
| 実行・retry/restart・W&B | experiment、trial、fold、attempt、旧output、実行記録 | `run-lifecycle.md` |
| 投入後の自動要約 | 最終評価job、対象attempt、成果物、要約保存先、Codex認証、後続job ID | `run-lifecycle.md` |
| 複数GPUでの実行 | Pueue group、割当GPU、device binding、attempt | `run-lifecycle.md` |
| Status・result | 必要成果物、current attemptへのprovenance | `run-lifecycle.md` |
