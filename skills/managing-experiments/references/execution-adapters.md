# Optional Execution and Notification Adapters

## 選び方

管理スキル本体は実行backendにも通知サービスにも依存しない。環境に既存し、ユーザーが利用する方式だけを選ぶ。未導入ツールのinstall・認証・常駐起動を通常の実験開始条件にしない。

| 環境 | 動作 |
|---|---|
| Pueueなし、通常のコマンド／既存runner | 既存方法で承認済み範囲を実行し、process・run記録・成果物を確認後に要約する。queue jobは作らない |
| Pueueあり、Discord未設定 | 通常の投入・評価・summaryを行い、外部通知だけ省略する |
| 別schedulerあり | 既存の依存・資源予約・ログ取得を使う。外部Pueue adapterを適用しない |
| Pueue＋Discordを承認・設定済み | 明示登録した新規実験だけを設定済みwatcherで通知する |
| Tailscaleなし | 実験管理・通知とも制約にしない。必要な接続は既存経路を使う |

## Pueueを使う場合


Pueueを採用済みの複数GPUマシンでは、ユーザーから別の明示的な指示がない限り、複数experiment、fold、trialを独立した1-GPU jobで実行する。GPUが複数あることを理由に、DDP、DataParallel、model sharding、1 jobでの複数GPU利用を選ばない。

投入前にGPUの台数、model、VRAM、稼働状況と、Pueueのgroup、`parallel`、既存の投入wrapperを検査する。GPUごとに固定groupを1つ対応させ、各groupを`parallel=1`にする。投入wrapperまたはtaskの環境で対応GPUを`CUDA_VISIBLE_DEVICES`へbindし、すべてのGPU jobを対応group経由に統一する。

```bash
pueue add --group gpu-0 --label 042c-fold0 \
  'CUDA_VISIBLE_DEVICES=0 uv run python scripts/train.py experiment=042_full_ft trial_id=042c fold=0'
```

Repository固有のgroup名、entrypoint、config overrideに置き換える。Pueue groupはそれ自体ではGPUをbindせず、`parallel=1`も同じgroup内だけを制限する。複数groupを同じGPUへ対応させたり、group外から直接GPU jobを起動したりすると相互排他が崩れる。Pueue採用環境でgroup等が未設定なら、その運用を無断で迂回せず必要な設定を確認する。Pueueを採用していないPCにはこの条件を適用せず、既存の実行方法を使う。

実行ごとにPueue job ID、group、割当GPU、GPU model、host、launch commandをresolved configまたはrun記録へ残す。同じ条件のretryを別GPUへ移す場合も、experiment・trial・foldを維持し、旧実行の出力を混在させない。

ユーザーがDDPまたは1 jobでの複数GPU利用を明示的に指示した場合だけ、repositoryの対応状況と比較条件への影響を別途調査して設計する。この指示がない状態でdistributed実行を実装、設定、投入しない。

## PueueとCodex CLIでの後続要約

この方式を採用済みの場合だけ、以下を使う。通常の対話内要約や別backendにCodex CLIを必須化しない。

- Codexの作業directoryを対象repositoryにし、GPUを予約しないgroupへ投入する。Pueueの`--after`は先行jobが成功した場合だけ起動する。失敗時の要約も必要なら終了callback等を使う。
- Promptは後続jobの`codex exec`へ渡す。`--ephemeral`は使わず、`--json`の出力とstderrをPueueのjobログに残す。Pueueはstdinを開いたままにするため、`codex exec ... </dev/null`として追加入力待ちを防ぐ。別のログファイルへ重複保存しない。
- 応答の`thread.started`に含まれるセッションIDを要約job IDと一緒に既存の実行記録へ残し、`pueue log <要約job ID>`で応答を追えるようにする。起動前に失敗してIDがなければ、その失敗を記録する。
- CLIで探す場合は`codex resume --all --include-non-interactive`を使う。通常の一覧では非対話セッションや別directoryのセッションが隠れる。IDが分かれば`codex resume <セッションID>`で開く。

## PueueとDiscordの通知adapter

[通知登録インターフェース](notification-interface.md)は、別repositoryのlab-notify/experiment_notificationsにある任意adapterの契約を示す。実装はこのskillに同梱せず、ホストに配置済みの場合だけ使う。genericは台帳形式の指定であり、任意のschedulerを操作するbackendではない。別backendに通知連携がなければ通知を省略し、実験を止めない。

外部adapterの設定例は既定で無効。競技名や指標の例、特定ホストの稼働設定を全PCの規則にしない。wsではこのadapterを有効化しているが、URL・承認時刻・有効フラグ・repo path・送信台帳はwsローカルにある。他PCへskillを配ってもadapterは自動導入しない。必要な場合はそのPCで承認された既存の導入手順に従い、秘密・有効設定・送信台帳をコピーしない。Tailscaleは依存しない。

Linux user systemdのservice例はその方式を選ぶ場合だけ使う。Mac／Windowsや別の常駐方式にsystemdを要求しない。Pueue実行ファイルの所在は環境に合わせる。実送信の宛先設定・秘密保存・常駐有効化は各環境で承認された範囲だけにする。
