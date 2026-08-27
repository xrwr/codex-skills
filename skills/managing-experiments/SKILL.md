---
name: managing-experiments
description: Use when a repository task explicitly concerns an experiment or run, including creating experiment configs, planning an ablation or baseline, changing experimental configuration, reproducing an experiment, retrying or restarting a run, or checking experiment status or results.
---

# Managing Experiments

## Overview

実験設定を自己完結させ、runの状態を現在のattemptに帰属する成果物で判定する。既存repositoryの契約を正本とし、一般的なDataset実装などexperiment config・run・結果管理を扱わない依頼には適用しない。

## Workflow

1. Repository、config、scripts、tests、output、log、job stateを先に検査する。実在する契約と不明点を分ける。
2. 依頼されたexperimentの仮説、入力、split、意味上の変更、必要成果物を特定する。
3. Config作成・変更では[config architecture](references/config-architecture.md)を読む。experiment configを自己完結したselection manifestにする。
4. 実行、retry/restart、status/result確認では[run lifecycle](references/run-lifecycle.md)を読む。experimentとattemptを分離し、成果物のprovenanceを検証する。
5. 変更範囲、確認済み証拠、未解決事項を報告する。依頼のないstart、stop、delete、submitを行わない。

Hydra、pueue、W&B、Lightningなどはrepositoryに既存し、現在利用可能な場合だけ使う。導入や必須化を推測しない。

## Quick Reference

| 依頼 | 必ず確認するもの | 読む参照 |
|---|---|---|
| Experiment config・ablation・baseline | defaults、component所有者、resolved config | `config-architecture.md` |
| 実行・retry/restart | experiment ID、attempt ID、旧output、実行記録 | `run-lifecycle.md` |
| Status・result | 必要成果物、current attemptへのprovenance | `run-lifecycle.md` |

## Common Mistakes

- 別experimentをdefaultsで継承する: 必要なcomponent selectionを新configへ展開する。
- Queueの`Done`やcheckpointだけで完了とする: 必要成果物の契約と帰属を確認する。
- 同じ仮説のretryへ新experiment IDを振る: experiment IDを維持し、新attemptとして記録する。
- Tool名から運用を決める: repositoryの既存scriptと状態を先に読む。

## Red Flags

- 「DRYだから」という理由だけでexperiment configを継承する
- 古いartifactとcurrent runのartifactを同じoutputで混在させる
- 欠けた証拠を推測で`verified`にする
- 依頼なしにjobやartifactへ破壊的操作を行う
