---
name: managing-experiments
description: Use when a repository task explicitly concerns an experiment or run, including creating experiment configs, planning an ablation or baseline, changing experimental configuration, reproducing an experiment, retrying or restarting a run, or checking experiment status or results.
---

# Managing Experiments

Experimentを仮説と検証計画、trialをその条件として管理する。既存repositoryの契約を正本とし、実行履歴はjob／run ID等で追う。人手のattempt採番や新しい管理階層を必須にしない。

## 環境に依存しない基本形

計画・実行・評価・要約が本体。実行方法はそのPC／repositoryの既存手順（通常のコマンド、既存runner、scheduler等）を使う。Discord・Pueue・Tailscale・特定ホストやpathは必須ではない。未導入なら勝手なinstall・認証・接続設定を前提にせず、通知未設定なら通知だけ省略する。環境別連携は[任意adapter](references/execution-adapters.md)を必要な場合だけ読む。

## 必須ゲート

- 新実験・未承認の仮説変更では、実験設定を作る前に、ユーザーに仮説を尋ねるか、根拠・比較方法を添えた仮説案を提示して承認を得る。確認前は既存資料の調査とチャットでの提案に留め、新規config・override・実験用コードの作成や変更を進めない。承認後に設定作成・静的検証を行い、実行範囲の許可を確認して投入する。保留・予約jobも投入に含む。承認済みの仮説・計画・予算内では毎回確認し直さず、各trialに独立した仮説の承認を要求しない。範囲を超える変更は再確認する。
- 採番と実行許可は分ける。retryはexperiment・trial・foldを維持し、既存成果物と人間の変更を保全する。投入前に既存jobを確認して重複を防ぐ。
- 設定・コード・入力／split・評価・成果物の対象実行への帰属を確認する。終了コードやcheckpointだけでverifiedにしない。事前仮説の欠落を結果から補わず、記録済みの探索と区別する。
- 依頼のないstart・stop・delete・submitや重い評価をしない。Hydra、pueue、W&B、Lightning等はrepositoryで既存かつ利用可能な場合だけ使う。
- 結果の事実と考察を分け、要約・知見はsummarizing-experimentsの契約に従う。通知の準備は秘密保存・外部送信・常駐有効化の許可を意味しない。

## ライフサイクル

必要な段階の参照だけを読む。最初にrepository・config・scripts・tests・outputs・log・job stateを調べ、実在する契約と不明点を分ける。

| 段階 | 確認・実施すること | 参照 |
|---|---|---|
| 仮説確認・計画・採番 | 過去実験を調べ、ユーザーから仮説を受け取るか仮説案を提示して承認を得る。番号候補・比較方法・予算を示し、確認前に実験設定を作らない | [計画と承認](references/planning-and-approval.md) |
| 設定・静的検証 | 仮説確認後に承認範囲とtrialの役割を記録し、既存schemaと配置に合わせて設定を作成する。自己完結したselection、解決後設定、基準との差分、出力先を検証する | [設定構成](references/config-architecture.md) |
| 投入・実行 | 既存の実行方法、資源割当、process／job／run ID、実行記録を確認。補助記録は本実験output外に置く | [実行手順](references/run-lifecycle.md) |
| 状態確認・retry | 必要成果物と帰属を照合し、採用済み結果を保持して同じ条件の履歴へ結び付ける | [実行手順](references/run-lifecycle.md) |
| 評価・要約・通知 | 実行計画に評価後の要約を含める。対応するqueueがある場合だけsummary jobを登録。通知は対応adapterが承認・設定済みの場合だけ使う | [終了処理](references/completion-and-notification.md) |

最後に、変更範囲、確認した証拠、未解決事項、要約jobと通知登録の状態（該当時）を報告する。既存の実験投入を通知のために停止・再実行しない。

通知設定済みの投入は登録結果とsummary確認への接続を確認する。通知は短い通常テキストを標準とし、ラベルだけ太字にする。具体的な契約は[通知インターフェース](references/notification-interface.md)を参照。

既存の閲覧先が設定された環境では、完了通知末尾に確認済みレポートリンクを任意で添える。Atlas未設定・到達不可ならリンクだけ省略し、実験管理と通知は続ける。公開範囲を無断で増やさない。

## ws の通知コード配置

ws では実験通知・共通Discord送信・Kaggle提出監視の正本を `~/Projects/work/lab-notify` に置く。旧 `scripts/experiment_notifications` は同じ実体への互換symlinkであり、二重編集しない。秘密・設定・通知済み状態は従来の `~/.config/experiment-notify` と `~/.local/state/experiment-notify` を保持する。提出監視は独立した任意サービスで、実験の開始・停止・提出操作を行わない。


## 共通起動チェックと明示通知skip

通知設定済みホストの通常実験は、新規jobを保留作成→台帳確定→ローカル通知登録を確認→解放の共通経路を使う。wsでは `workflow.json` の `launch_registration_required=true` により、登録失敗時は新規jobを保留のままにする。既存jobを停止・再解放しない。Discordの送達成功は起動条件にせず、外部送信障害で学習を止めない。

短いsmoke/debug等は呼出側で `--skip-notifications` を明示できる。任意の `--notification-skip-reason smoke` とともに台帳へ `notification.status=skipped`・`explicit=true` を記録し、未登録事故と区別する。時間閾値で自動除外しない。skipは実験実行の承認を代替しない。後付け登録の `start_suppressed` を通常起動で使用しない。

coreは `lab-notify/experiment_notifications/launch_guard.py`。登録ID・台帳・job集合・開始抑止なしを永続DBと照合する。解放前にclaimを残し、二重解放や解放結果不明の自動再試行を防ぐ。adapter未設定かつ必須化していないPCではdisabledを記録して通常実行でき、Discord・Pueue・Tailscaleをcoreの必須依存にしない。

保証は共通経路の新規起動内だけ。直接python/pueueや未対応launcherをOSで禁止しない。開始通知は現行60秒Running観測のため短時間実行を見逃し得る。queue全体からの自動登録・遡及通知は行わない。起動失敗後の再開は保存されたjobとclaimを確認して別途扱う。
