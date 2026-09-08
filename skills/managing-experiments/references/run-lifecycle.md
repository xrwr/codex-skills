# Run Lifecycle

## Identity

| 単位 | 意味 |
|---|---|
| experiment | 実験全体で判断する仮説と、その検証計画。複数trialを通じて結論を出す |
| trial | 検証計画内の具体的な条件。設定・seedなどの組合せを特定する |
| fold | 決めたCV計画の内訳。fold違いだけではtrialを増やさない |
| attempt | 同じtrial、CVなら同じfoldの実行履歴。retryでは新しくする |

テーマ名・テーマIDを必須の管理階層として追加しない。以下のID名・表記は例であり、repositoryの既存schemaを優先する。

### 仮説と検証計画

仮説は観測や既知の根拠から立て、何が成り立つと予想し、どの比較結果なら支持・不支持・保留かを開始前に記録する。実験全体の主張と、次のtrialを選ぶ局所的な予想を区別する。「係数0.01ならよさそう」という予想や先例の細かい実験YAMLだけを根拠に採番しない。

計画には比較対象、固定条件、具体的な変更軸・探索範囲、試行数や時間の予算、評価方法・判定条件を持たせる。「性能改善全般」のような無制限の範囲にしない。trialごとに仮説の何を確かめるかと基準条件からの差を残す。

仮説生成を目的とする明示的な探索では、探索目的・範囲・予算・評価方法を事前記録し、各候補に根拠のない方向仮説を作らない。探索で得た傾向と、その後の仮説検証を区別する。通常の仮説検証を、記録を省くために探索と呼び替えない。

### 採番の判断

新しいexperimentを作る前に、最新だけでなく過去の実験記録を仮説・比較対象・検証範囲から検索する。

| 次の作業 | 判断 |
|---|---|
| 計画内の変更軸の値を変える | 同じexperimentにtrialを追加する |
| 同じ軸の探索範囲を広げる | 主仮説と固定条件が同じなら計画の変更理由・時点・追加予算を記録する。既存の実行許可の上限は超えない |
| 同じ条件でやり直す | experiment・trial・foldを維持して新attemptにする |
| 主仮説、固定条件や比較の意味を変える | 該当する既存experimentがなければ、新experimentとする理由を記録して採番する |
| 有望なtrialを出発点に独立した調整計画を始める | 新experimentへ派生させ、基準experiment・trial・成果物を記録する |
| 動作確認や実装不具合の切り分け | 対象実験の補助記録にし、作業のたびにexperimentを作らない |

変更の大小・実行時間・コードの行数で判断しない。層数3→4が002の計画内なら、最新が030でも002にtrialを追加する。一方、031が複数モデル方式を比較する計画なら、大きな方式変更も031内の候補である。その候補を独立して調整する032は`031/t002`など具体的な出発点へ紐付ける。元trialの移動・改番や、trialの下への無制限なtrial階層の追加は不要。

古いexperimentに戻る場合は、基準trial、コード版、resolved config、入力・split・評価方法を復元して比較可能性を確認する。現在のdefaultsやコードを暗黙に混ぜない。固定条件の変更を採用する場合はその比較計画を別experimentとして扱い、必要な基準の再評価を行う。過去の仮説・結果・IDは保持し、今回追加する計画を当時の事前記録として扱わない。旧記録にtrialがなければ基準条件への対応を今回記録し、成果物を推測で再番号付けしない。

### 実行記録

trial IDはexperiment内、attempt IDはtrialとfold内で一意にし、実行はそれらの組で特定する。並列投入では既存の採番・登録経路で重複を防ぐ。各attemptに全識別子、実際の設定、コード版、データ・評価の識別情報、コマンド、状態、指標、成果物の場所、外部run IDを記録する。単なる不具合修正なら同じ条件の新attemptにできるが、修正前の結果が無効ならその理由を残す。計算や評価の意味を変える修正は採番の判断へ戻る。

記録先は既存の台帳・CSV・DBなどを使う。軽い試行は機械的な行記録でよく、trialごとの手書きYAML・説明ファイルを要求しない。checkpoint等が必要なら、例えば`outputs/<experiment>/<trial>/[fold-N/]<attempt>/`へ保存する。旧attemptを上書きせず、実際に読み書きするpathと設定を一致させる。

## W&Bを使用する場合

- 既存projectを使い、configにexperiment・trial・fold（該当時）・attemptを保存する。run名は`042_capacity-t003_depth4-fold0-a02`のように、実験名と条件差を読める形にする。原則1attemptを1runとして一意なW&B run IDを台帳へ残す。
- `group`は同一trial・同一評価計画のCV fold集合に使う（例：`042-t003`。同じproject内のtask間でも衝突させない）。異なるtrialをexperiment IDだけで一括groupにしない。CV以外はgroupを設定せず、チャートのrun集約も行わない。
- retryを含む全runの平均をCV結果にしない。各foldの採用attemptを成果物の検証に基づいて記録し、CV集計・平均曲線にはその集合だけを使う。途中で失敗したfoldのretryによって、他foldの採用結果を消したり重複計上したりしない。fold指標の平均とOOF全体で計算した指標は区別する。
- W&Bのrun一覧の件数を減らすための概要専用run・専用ビュー・別projectへの移動は、この管理方式の要件にしない。既存runのgroupやIDを一括で書き換えない。
- 軽い探索で必要なら、上限を定めた1バッチを1runとし、trial・attempt・条件・状態・結果をTableの行とローカル記録で対応させてもよい。複数条件を一つの学習曲線として混ぜない。
- 既存のcheckpoint再開で同じW&B runを継続する契約がある場合は、その継続と最初からのやり直しを区別し、ローカルのattempt境界・再開元・stepを残す。

W&Bの[group](https://docs.wandb.ai/models/runs/grouping)と[チャートの集約](https://docs.wandb.ai/models/app/features/panels/line-plot/reference#run-grouping)は別に確認する。group属性だけでは、retryの除外や意図した集計は保証されない。

## GPU Resource Contract

複数GPUマシンでは、ユーザーから別の明示的な指示がない限り、Pueueを既定として複数experiment、fold、trialを独立した1-GPU jobで実行する。GPUが複数あることを理由に、DDP、DataParallel、model sharding、1 jobでの複数GPU利用を選ばない。

投入前にGPUの台数、model、VRAM、稼働状況と、Pueueのgroup、`parallel`、既存の投入wrapperを検査する。GPUごとに固定groupを1つ対応させ、各groupを`parallel=1`にする。投入wrapperまたはtaskの環境で対応GPUを`CUDA_VISIBLE_DEVICES`へbindし、すべてのGPU jobを対応group経由に統一する。

```bash
pueue add --group gpu-0 --label 042-t003-fold0-a01 \
  'CUDA_VISIBLE_DEVICES=0 uv run python scripts/train.py experiment=042_full_ft trial_id=t003 fold=0 attempt_id=a01'
```

Repository固有のgroup名、entrypoint、config overrideに置き換える。Pueue groupはそれ自体ではGPUをbindせず、`parallel=1`も同じgroup内だけを制限する。複数groupを同じGPUへ対応させたり、group外から直接GPU jobを起動したりすると相互排他が崩れる。Pueueが未設定なら勝手にDDPや直接実行へ切り替えず、必要なgroupとbinding方法を提案して未実行とする。

AttemptごとにPueue job ID、group、割当GPU、GPU model、host、launch commandをresolved configまたはrun記録へ残す。同じ条件のretryを別GPUへ移す場合も、experiment・trial・foldを維持して新attemptとし、旧attemptの出力を混在させない。

ユーザーがDDPまたは1 jobでの複数GPU利用を明示的に指示した場合だけ、repositoryの対応状況と比較条件への影響を別途調査して設計する。この指示がない状態でdistributed実行を実装、設定、投入しない。

## Artifact Evidence

依頼とrepositoryから、必要artifact contractを先に確定する。YAML、job、process終了、checkpointの存在だけでexperimentをcompleteまたはverifiedにしない。Artifactのrun ID、resolved config、log、timestamp、生成記録を照合し、current attemptへ帰属できる証拠だけを使う。

| 状態 | 必要な証拠 |
|---|---|
| `queued` | Queueへ登録済みで、開始していない記録 |
| `running` | Current attemptのactive processまたは更新中のlog |
| `failed` | Current attemptのerror、非正常終了、または失敗記録 |
| `partial` | 帰属確認済みartifactはあるが、必要artifact contractが未充足 |
| `verified` | 必要artifactがすべて存在し、検証済みで、current attemptへ帰属する |
| `unknown` | 証拠がない、古い、または相互に矛盾する |

Job manager、tracking service、framework固有の状態は、それらがrepositoryで既存かつ利用可能な場合だけ補助証拠にする。

## Retry Procedure

1. experimentの仮説・検証計画と、対象trial・foldの条件が同じか確認する。
2. 旧attemptのresolved config、log、checkpoint、metricを記録する。
3. 旧outputがattempt別ならそのまま保持する。canonical outputを再利用する契約なら、対象trial・foldの旧attemptだけを退役先へarchiveする。他trial・成功foldを巻き込まない。
4. 同じexperiment・trial・foldと新attemptで、空の出力先を使う。外部runの継続は既存の再開契約と照合する。
5. 新artifactのprovenanceと必要artifact contractを再検証する。

## 補助記録の保存先

本実験のoutputツリーには、本実験のcheckpoint・metric・predictionなどだけを置く。学習前チェック、GPU監視の追加ログ、Codexの実行ログ・一時ファイルは、outputツリーの外へ置く。既存の専用場所がなければrepository直下の`.cache/experiment-tools/<experiment>/<trial>/[fold-N/]<attempt>/`など衝突しない場所を使い、Gitの追跡対象外にする。`outputs/pretrain/debug/`のようにoutput内で分けるだけでは不十分。

補助記録は再確認に必要な最小限にし、既存logやconfigを複製しない。ユーザー向けの最終要約は既存の実験ドキュメントへ保存する。

## Completion Summary

- 単独検証、または対象trialと上限を事前に定めた探索バッチの投入時に、必要な評価の完了後にCodexで結果を要約するjobも登録する。短い探索の各trial・各foldに要約jobを増殖させず、バッチの記録を集計して同じexperimentのサマリを更新する。バッチ完了をexperimentの仮説検証完了と同一視しない。要約不要の指定があれば省く。
- 起動先で`summarizing-experiments`が利用可能なことを確認し、要約方法はそのスキルに任せる。未導入なら長い代替promptを作らず、未設定として報告する。
- Promptは「実験042の結果をまとめて」程度の一文にする。再実行が複数あり対象が曖昧な場合だけ、既存のrun名や成果物のpathを足す。スキル本文の転記やprompt専用ファイルの作成は不要。
- Codexの作業directoryを対象repositoryにし、GPUを予約しないgroupへ投入する。Pueueの`--after`は先行jobが成功した場合だけ起動する。失敗時の要約も必要なら終了callback等を使う。
- Promptは後続jobの`codex exec`へ渡す。`--ephemeral`は使わず、`--json`の出力とstderrをPueueのjobログに残す。Pueueはstdinを開いたままにするため、`codex exec ... </dev/null`として追加入力待ちを防ぐ。別のログファイルへ重複保存しない。
- 応答の`thread.started`に含まれるセッションIDを要約job IDと一緒に既存の実行記録へ残し、`pueue log <要約job ID>`で応答を追えるようにする。起動前に失敗してIDがなければ、その失敗を記録する。
- CLIで探す場合は`codex resume --all --include-non-interactive`を使う。通常の一覧では非対話セッションや別directoryのセッションが隠れる。IDが分かれば`codex resume <セッションID>`で開く。
- 対象trial・fold・attemptの集合と後続job IDを既存の実行記録へ残す。失敗trial・不足foldがあれば、その欠落を集計に残す。自動処理は結果の要約までとし、個別サマリと全体の系統図・一覧表の更新を確認して完了とする。

依頼なしにrunをstart/stopせず、outputやartifactをdeleteしない。破壊的操作が必要なら対象と影響を示して承認を求める。
