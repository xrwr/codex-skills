---
name: checking-training-pipelines
description: Use when validating a neural-network training pipeline before a full run, after changes to data, model, loss, or training code, or when asked for 学習前チェック, リークチェック, forward smoke test, one-batch overfit, a short debug run, or diagnosing training slowdown and GPU utilization.
---

# Checking Training Pipelines

実際のデータと既存の学習経路で、次の順に本学習前の確認をする。時間・更新step数・検証件数に上限を設ける。

## チェック

1. **Leak check**: 評価目的に合うgroup単位でsplitの重複、前処理のfit範囲、教師・未来情報の混入を確認する。
2. **Forward smoke test**: 実batchの入力・教師・予測のshapeと意味を確認し、有限のloss・gradientとoptimizerによるparameter更新を確かめる。
3. **Overfit one batch**: Transform後のbatchを固定し、ランダムaugmentation等を止めて反復学習する。到達可能なloss水準と予測・教師の対応を確認する。
4. **短期debug**: 本学習用の初期状態と設定に戻し、少数batchで学習・評価・保存・再読込を通す。全epochや全件validationは必須にしない。短時間でのvalidation loss改善を合格条件にせず、汎化性能の確認が必要な場合だけ追加pilotを行う。

失敗や必要な確認の不足があれば後続を止め、短く報告する。終了コード0だけで合格にしない。変更した経路は再確認し、本学習まで依頼されていれば確認後に進める。

## 速度・GPU監視

- 既存logと低頻度の計測で、更新stepの所要時間・throughput、データ待ち、GPU使用率・VRAM・温度・電力を確認する。必要時だけCPU/I/Oや詳細profilerで原因を絞る。
- 初回compile、検証、保存の時間を学習区間と分け、同じ条件で持続的な速度低下を調べる。GPU使用率だけで正常性を判断しない。
- 本学習へ軽い計測を引き継ぎ、監視が学習を遅くしないようにする。速度調査だけの依頼では4段階を再実行しない。

## 記録

- Debug出力や追加の監視ログは**本実験のoutputツリーの外**に置く。既存の専用場所がなければrepository直下の`.cache/experiment-tools/<experiment>/<attempt>/`を使い、Gitの追跡対象外にする。`outputs/pretrain/`の下に補助directoryを並べない。
- 既存logを優先し、追加記録は判定・短い根拠・再実行command程度にする。大量のtensor、全stepの予測、configの複製、段階ごとの詳細レポートは既定で保存しない。診断に必要なものだけ補助領域へ残す。
- ユーザーには「進行可能・要修正・判断保留」と要点だけを返す。

参考: [A Recipe for Training Neural Networks](https://karpathy.github.io/2019/04/25/recipe/)
