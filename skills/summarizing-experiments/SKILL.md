---
name: summarizing-experiments
description: Use when summarizing, documenting, reporting, or comparing a repository's experiment history or an individual experiment.
---

# Summarizing Experiments

## Overview

事前記録された仮説とcurrent attemptに帰属する成果物を照合し、事実・解釈・未確認を分けて報告する。実験レポートを作成する前に、[report contract](references/report-contract.md)を必ず全文読む。

## Workflow

1. Repositoryの既存docs、config、artifact、metric、predictionと、それらの命名・保存・評価契約を先に調べる。特定framework、path、config schemaを持ち込まない。
2. 対象experiment、親、current attempt、比較条件を特定する。成果物のrun ID、resolved config、log、timestampなどを照合し、current attemptへ帰属する証拠だけを採用する。
3. 仮説と判定基準がlaunch以前に記録されたことをcommit、run snapshot、timestampなどで照合する。確認できなければ「記録時点不明」と明記し、事前仮説として扱わず判断保留にする。結果から仮説を後付けしない。
4. 必要な最終成果物が揃い、評価条件が比較可能か検証する。必要評価またはcurrent attemptの最終成果物がなければ`未評価`を優先する。Queueの`Done`、process exit、checkpointだけで結果をverifiedにしない。
5. 確認できた数値や条件を事実、そこから導く説明を解釈、証拠不足や矛盾を未確認として分ける。曖昧な場合は断定しない。
6. Repository全体では5列の一覧、各experimentでは個別サマリを作る。結果短文だけで`支持`、`反証`、`判断保留`、`未評価`の判定が分かるようにする。
7. 既存の文書構成と表記を優先する。規約がなければ`docs/experiments.md`と`docs/experiments/<id>.md`を提案し、合意なしに標準として強制しない。

## Quick Reference

| 対象 | 記録するもの | 判定の根拠 |
|---|---|---|
| 全体履歴 | 実験、親、仮説、結果、対象に合う主指標 | 比較可能なcurrent attemptの最終成果物 |
| 個別実験 | 要旨から次の判断までの詳細 | Config、metric、prediction、log |
| 証拠不足 | 未評価または判断保留と不足物 | 確認できた事実だけ |

## Common Mistakes

- 実行状態を結果として扱う: Repositoryが要求するmetricやpredictionを確認する。
- 古いattemptの成果物を混ぜる: Provenanceを照合し、帰属不能なら未確認にする。
- 表へ変更点や注釈を詰め込む: 一覧を5列に保ち、詳細を個別サマリへ移す。
- 指標値へ親との差分や矢印を書く: 絶対値だけを書く。
- 事後的な説明を事前仮説として書く: 仮説の欠落をそのまま報告する。

## Red Flags

- 比較するsplit、metric定義、評価条件が一致していない
- 主指標の出典またはcurrent attemptへの帰属を示せない
- 事実と解釈が一文に混在している
- 「改善した」と書いたが、判定基準が事前記録されていない
- 証拠不足を推測で埋めている
