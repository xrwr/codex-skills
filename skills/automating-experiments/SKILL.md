---
name: automating-experiments
description: Use only when the user explicitly requests starting, inspecting, or stopping an automatic experiment loop that hands summaries to fresh Codex sessions. Ordinary summaries and single experiment requests do not enable the loop.
---

# Automating Experiments

明示的に許可された範囲で、サマリー→次の検証→実行→要約を接続する。仮説と評価の解釈は`summarizing-experiments`、設定・投入・attempt管理は`managing-experiments`に任せる。自動化の準備や使い方の質問だけでは、実験を開始しない。

## 開始

1. 対象repositoryと目的、変更してよい範囲、GPU、実験の上限をユーザーの指示から決める。上限未指定なら最大3回として伝える。1回は追加検証1件の投入までで、retryも1回に数える。対象・目的が不明なら開始前に確認する。
2. 起動先で上記2スキルと本スキル、`codex exec`の認証、Pueueを確認する。GPUの割当は実験管理に従う。制御用の専用groupを使い、学習・評価・要約jobをこのgroupへ入れない。
3. [実行スクリプト](scripts/experiment_loop.py)の`start`へ、許可内容を`--scope`、上限を`--rounds`で渡す。状態は対象repositoryのGit追跡外の`.cache/experiment-tools/automation/<識別名>/state.json`などへ保存する。同じ状態の再起動や上限の自動延長はしない。

```bash
python3 <skill-dir>/scripts/experiment_loop.py start \
  --repo /path/to/project \
  --state /path/to/project/.cache/experiment-tools/automation/trial/state.json \
  --scope '検出器の見逃しを分析して改善を検証。GPU 0を使う。データ分割は固定。' \
  --rounds 3
```

Pueue上で制御jobが動き、各回は新しいCodexセッションになる。制御groupは既定で`experiment-automation`（なければ作成）。Codexは既存のモデル・認証設定と`--approve-for-me`を使う。承認拒否や実行失敗は停止として扱い、権限を広げる設定へ切り替えない。

## 各セッションの仕事

- 制御スクリプトが渡した状態と今回の回数を読み、許可範囲内で既存の全体・個別サマリーと根拠を確認する。未要約なら先に要約する。
- 次の推奨を選ぶ。仮説の確信が弱くても、根拠・予測・判定方法を記録して探索できる。評価の妥当性が不明なら、その確認を検証に選べる。理由のない学習の反復はせず、追加観察・保留・停止も選ぶ。
- 実験管理スキルで**追加検証を最大1件**投入し、必要な評価の後に要約jobを登録する。既存jobと成果物を確認し、同じ検証を重複投入しない。1回の中で失敗を自動retryしない。
- 要約jobは個別サマリーと全体の見立て・系統図・一覧を更新する通常の要約とする。次の実験や制御jobは投入させない。
- 投入したら、その要約job IDを制御スクリプト指定のJSON形式で返して終了する。要約jobの成功を制御側が待ってから次セッションを開く。終了コードだけで研究上の成功と判断せず、次セッションで成果物と更新内容を確認する。
- 進める検証がない、実行・要約登録が失敗した、許可範囲を超える場合は、理由と投入済みjobを記録して`stop`を返す。既存成果物や旧attemptを消して再開しない。

## 状態と停止

```bash
python3 <skill-dir>/scripts/experiment_loop.py status --state /path/to/state.json
python3 <skill-dir>/scripts/experiment_loop.py stop --state /path/to/state.json
```

`stop`は次回以降のセッションを止める。すでに始まったセッションと実験jobは終了まで続く。現在の学習自体を止める依頼があれば、実験管理で対象jobを別途扱う。

上限到達・停止・失敗の理由、制御job ID、各セッションIDと要約job IDは状態へ残す。詳細は`pueue log <制御job ID>`と各要約jobのログへ戻る。障害後は状態と投入済みjobを確認し、ユーザーの再開指示を受けて新しい状態を作る。
