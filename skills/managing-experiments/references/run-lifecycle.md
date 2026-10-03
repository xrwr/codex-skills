# Run Lifecycle

## Identity

| 単位 | 意味 |
|---|---|
| experiment | 実験全体で判断する仮説と、その検証計画。複数trialを通じて結論を出す |
| trial | 検証計画内の具体的な条件。設定・seedなどの組合せを特定する |
| fold | 決めたCV計画の内訳。fold違いだけではtrialを増やさない |

テーマ名・テーマIDを必須の管理階層として追加しない。以下のID名・表記は例であり、repositoryの既存schemaを優先する。

実行履歴はjob ID・run ID・log・設定snapshotで識別する。人手のattempt採番・専用directoryを必須にしない。既存repositoryがattemptを使う場合は、その契約と過去の記録を保持する。

### 条件IDの表記

新たに命名ルールを決める場合は、experimentの3桁の数字IDに小文字の英字を付けてtrialを識別する。実験`001`の条件は`001a`・`001b`・`001c`、実験`002`の最初の条件は`002a`とする。条件名は`001a_baseline`・`001b_lr_half`のように短く添えてよい。`z`の次が必要なら`aa`・`ab`と続ける。

条件を追加するときに次の英字を割り当て、fold違いや同条件のretryではtrial IDを維持する。通常の保存先は`outputs/001/001b/`、CVありなら`outputs/001/001b/fold-0/`とし、実行回の番号を階層に追加しない。旧結果の保持と実行の識別は下の実行記録・Retry Procedureに従う。

チャット・条件表・結果表・比較基準の参照では`001b`のようにexperimentと条件を一つのIDで示す。設定・台帳ではexperimentとtrialの項目を保ち、この方式を採用する新規schemaなら`experiment_id: "001"`・`trial_id: "001b"`とする。既存のschema・ID・成果物は保持し、表記変更だけを理由に移動・改番しない。既存repositoryへ導入する場合は、config・出力先・loggerの対応を確認して対象範囲を決める。

### 仮説と検証計画

仮説は観測や既知の根拠から立て、何が成り立つと予想し、どの比較結果なら支持・不支持・保留かを開始前に記録する。実験全体の主張と、次のtrialを選ぶ局所的な予想を区別する。「係数0.01ならよさそう」という予想や先例の細かい実験YAMLだけを根拠に採番しない。

計画には比較対象、固定条件、具体的な変更軸・探索範囲、試行数や時間の予算、評価方法・判定条件を持たせる。「性能改善全般」のような無制限の範囲にしない。開始前の仮説の確認はexperiment（`001`）単位で行い、trial（`001a`・`001b`）単位では独立した仮説や仮説への承認を必須にしない。trialごとに条件ID、上位仮説の何を確かめるか、比較基準と変更条件を残す。上位仮説・比較計画が変わる場合は、trial追加として進める前に採番の判断へ戻る。

仮説生成を目的とする明示的な探索では、探索目的・範囲・予算・評価方法を事前記録し、各候補に根拠のない方向仮説を作らない。探索で得た傾向と、その後の仮説検証を区別する。通常の仮説検証を、記録を省くために探索と呼び替えない。

### 採番の判断

新しいexperimentを作る前に、最新だけでなく過去の実験記録を仮説・比較対象・検証範囲から検索する。

[SKILL.mdの採番と確認の判断](../SKILL.md#採番と確認の判断)を適用する。新番号の候補を理由・実験全体の仮説・比較計画とともに開始前にユーザーへ知らせ、同参照の確認条件を満たしてから正式登録・実行する。「ミスを直して」「やり直せ」では対象experiment・trial・foldを維持し、失敗だけを理由に新IDを発行しない。動作確認や実装不具合の切り分けは対象実験の補助記録とする。固定条件や比較の意味を意図的に変える場合は、該当する既存計画がなければ新experimentとし、基準trial・成果物を記録する。採番が必要かと、実行が許可されているかは別に確認する。

変更の大小・実行時間・コードの行数で判断しない。層数3→4が002の計画内なら、最新が030でも002にtrialを追加する。一方、031が複数モデル方式を比較する計画なら、大きな方式変更も031内の候補である。その候補を独立して調整する032は`031b`など具体的な出発点へ紐付ける。元trialの移動・改番や、trialの下への無制限なtrial階層の追加は不要。

古いexperimentに戻る場合は、基準trial、コード版、resolved config、入力・split・評価方法を復元して比較可能性を確認する。現在のdefaultsやコードを暗黙に混ぜない。固定条件の変更を採用する場合はその比較計画を別experimentとして扱い、必要な基準の再評価を行う。過去の仮説・結果・IDは保持し、今回追加する計画を当時の事前記録として扱わない。旧記録にtrialがなければ基準条件への対応を今回記録し、成果物を推測で再番号付けしない。

### 実行記録

trial IDはexperiment内で一意にし、各実行はjob／run IDなど既存の実行記録で特定する。並列投入では既存の採番・登録経路で重複を防ぎ、同じtrial・foldの保存先へ同時に書き込まない。各実行にexperiment・trial・fold、実際の設定、コード版、データ・評価の識別情報、コマンド、状態、指標、成果物の場所、job／run IDを記録する。修正前の結果が無効なら理由を残し、新結果と混ぜない。計算や評価の意味を変える修正は採番の判断へ戻る。

記録先は既存の台帳・CSV・DBなどを使う。軽い試行は機械的な行記録でよく、trialごとの手書きYAML・説明ファイルを要求しない。checkpoint等は、既存規約がなければ`outputs/<experiment>/<trial>/[fold-N/]`へ保存する。採用済み・比較に使った結果を再実行で失わず、実際に読み書きするpathと設定を一致させる。

仮説・承認範囲は既存の実験ドキュメントへ、実行設定は既存entrypointが読むconfigへ、実行の状態・成果物への参照は既存の実行記録へ保存する。失敗→修正→完了の履歴は同じ条件へ紐付ける。Metricやresolved configは既存writerの形式で出力する。

結果欄には確認できた事実と未確認事項を記録し、原因の推測や次の推奨を混ぜない。事後の考察はチャットで示し、実験結果に基づく重要な比較結論は個別の許可を求めず`docs/knowledge/`など既存の知見保存先へ短く記録する。判定・粒度と未検証アイデアの保存は要約スキルの契約に従う。

Commit IDを実験文書のヘッダーの必須項目にせず、記録のためだけのcommitも要求しない。Hydraを使う場合は各実行に対応する`.hydra/config.yaml`・`hydra.yaml`・`overrides.yaml`と既存のresolved configを再利用する。`.hydra`の保存が有効か、実行時の補間値まで確定した設定が残るかを確認し、不足分だけ既存writerで保存する。Hydraの設定記録はコードの保存ではないため、コード版は既存のコードsnapshotや、commitと未コミット差分などで識別する。必要なコード状態を確認できなければ未確認と記し、設定だけで完全な再現性を保証しない。

出力構成は[開始前の提案と確認](../SKILL.md#実験開始前の提案と確認)に含める。既存の出力階層を使い、学習・評価・logger・checkpointのwriterが実際に使うpathを設定と実装から確認する。Trial・foldごとの出力先を一意にし、旧実行との混在を防ぐ。補助記録は専用の保存先へ対応付ける。解決したpathを案として提示し、承認後に実行用directoryを作成する。

## W&Bを使用する場合

- 既存projectを使い、configにexperiment・trial・fold（該当時）を保存する。run名は`042c_capacity_depth4-fold0`のように、実験名と条件差を読める形にする。原則1実行を1runとし、一意なW&B run IDを台帳へ残す。run名への手動の実行回番号は要求しない。
- `group`は同一trial・同一評価計画のCV fold集合に使う（例：`042c`。同じproject内のtask間でも衝突させない）。異なるtrialをexperiment IDだけで一括groupにしない。CV以外はgroupを設定せず、チャートのrun集約も行わない。
- retryを含む全runの平均をCV結果にしない。各foldの採用結果と対応するrun IDを成果物の検証に基づいて記録し、CV集計・平均曲線にはその集合だけを使う。途中で失敗したfoldのretryによって、他foldの採用結果を消したり重複計上したりしない。fold指標の平均とOOF全体で計算した指標は区別する。
- W&Bのrun一覧の件数を減らすための概要専用run・専用ビュー・別projectへの移動は、この管理方式の要件にしない。既存runのgroupやIDを一括で書き換えない。
- 軽い探索で必要なら、上限を定めた1バッチを1runとし、trial・実行記録・条件・状態・結果をTableの行とローカル記録で対応させてもよい。複数条件を一つの学習曲線として混ぜない。
- 既存のcheckpoint再開で同じW&B runを継続する契約がある場合は、その継続と最初からのやり直しを区別し、実行履歴・再開元・stepを残す。

W&Bの[group](https://docs.wandb.ai/models/runs/grouping)と[チャートの集約](https://docs.wandb.ai/models/app/features/panels/line-plot/reference#run-grouping)は別に確認する。group属性だけでは、retryの除外や意図した集計は保証されない。

## GPU Resource Contract

複数GPUマシンでは、ユーザーから別の明示的な指示がない限り、Pueueを既定として複数experiment、fold、trialを独立した1-GPU jobで実行する。GPUが複数あることを理由に、DDP、DataParallel、model sharding、1 jobでの複数GPU利用を選ばない。

投入前にGPUの台数、model、VRAM、稼働状況と、Pueueのgroup、`parallel`、既存の投入wrapperを検査する。GPUごとに固定groupを1つ対応させ、各groupを`parallel=1`にする。投入wrapperまたはtaskの環境で対応GPUを`CUDA_VISIBLE_DEVICES`へbindし、すべてのGPU jobを対応group経由に統一する。

```bash
pueue add --group gpu-0 --label 042c-fold0 \
  'CUDA_VISIBLE_DEVICES=0 uv run python scripts/train.py experiment=042_full_ft trial_id=042c fold=0'
```

Repository固有のgroup名、entrypoint、config overrideに置き換える。Pueue groupはそれ自体ではGPUをbindせず、`parallel=1`も同じgroup内だけを制限する。複数groupを同じGPUへ対応させたり、group外から直接GPU jobを起動したりすると相互排他が崩れる。Pueueが未設定なら勝手にDDPや直接実行へ切り替えず、必要なgroupとbinding方法を提案して未実行とする。

実行ごとにPueue job ID、group、割当GPU、GPU model、host、launch commandをresolved configまたはrun記録へ残す。同じ条件のretryを別GPUへ移す場合も、experiment・trial・foldを維持し、旧実行の出力を混在させない。

ユーザーがDDPまたは1 jobでの複数GPU利用を明示的に指示した場合だけ、repositoryの対応状況と比較条件への影響を別途調査して設計する。この指示がない状態でdistributed実行を実装、設定、投入しない。

## Artifact Evidence

依頼とrepositoryから、必要artifact contractを先に確定する。YAML、job、process終了、checkpointの存在だけでexperimentをcompleteまたはverifiedにしない。Artifactのrun ID、resolved config、log、timestamp、生成記録を照合し、対象実行へ帰属できる証拠だけを使う。

| 状態 | 必要な証拠 |
|---|---|
| `queued` | Queueへ登録済みで、開始していない記録 |
| `running` | 対象実行のactive processまたは更新中のlog |
| `failed` | 対象実行のerror、非正常終了、または失敗記録 |
| `partial` | 帰属確認済みartifactはあるが、必要artifact contractが未充足 |
| `verified` | 必要artifactがすべて存在し、検証済みで、対象実行へ帰属する |
| `unknown` | 証拠がない、古い、または相互に矛盾する |

Job manager、tracking service、framework固有の状態は、それらがrepositoryで既存かつ利用可能な場合だけ補助証拠にする。

## Retry Procedure

1. 採番の判断表で、対象trial・foldの修正・再実行か、条件変更かを分類する。許可範囲・残り予算と既存jobを確認する。判断に迷う場合は確認する。
2. 旧実行のjob／run ID、resolved config、log、状態を記録する。無効な結果には理由を残す。
3. 採用済み・比較に使った結果と必要な旧成果物は、既存の保持・archive方法で保存する。必要なら既存job／run IDで退役先を識別する。対象trial・foldだけを扱い、他trial・成功foldを巻き込まない。既存のattempt別保存先はそのまま保持する。
4. 同じexperiment・trial・foldで実行する。最初からやり直す場合は古いmetric・prediction・checkpointを新結果へ混ぜない出力先を用意する。途中再開の場合は指定checkpointと既存の再開契約に従う。
5. 実行履歴と状態を更新し、新artifactのprovenanceと必要artifact contractを再検証する。失敗を理由に実験番号を捨てたり振り直したりしない。

## 補助記録の保存先

本実験のoutputツリーには、本実験のcheckpoint・metric・predictionなどだけを置く。学習前チェック、GPU監視の追加ログ、Codexの実行ログ・一時ファイルは、outputツリーの外へ置く。既存の専用場所がなければrepository直下の`.cache/experiment-tools/<experiment>/<trial>/[fold-N/]`などを使い、並行する補助処理の記録は既存job ID等で衝突を防ぐ。Gitの追跡対象外にする。`outputs/pretrain/debug/`のようにoutput内で分けるだけでは不十分。

補助記録は再確認に必要な最小限にし、既存logやconfigを複製しない。ユーザー向けの最終要約は既存の実験ドキュメントへ保存する。

## Completion Summary

- 単独検証、または対象trialと上限を事前に定めた探索バッチの投入時に、必要な評価の完了後にCodexで結果を要約するjobも登録する。短い探索の各trial・各foldに要約jobを増殖させず、バッチの記録を集計して同じexperimentのサマリを更新する。バッチ完了をexperimentの仮説検証完了と同一視しない。要約不要の指定があれば省く。
- 起動先で`summarizing-experiments`が利用可能なことを確認し、要約方法はそのスキルに任せる。未導入なら長い代替promptを作らず、未設定として報告する。
- Promptは「実験042の結果をまとめて」程度の一文にする。再実行が複数あり対象が曖昧な場合だけ、既存のrun名や成果物のpathを足す。スキル本文の転記やprompt専用ファイルの作成は不要。
- Codexの作業directoryを対象repositoryにし、GPUを予約しないgroupへ投入する。Pueueの`--after`は先行jobが成功した場合だけ起動する。失敗時の要約も必要なら終了callback等を使う。
- Promptは後続jobの`codex exec`へ渡す。`--ephemeral`は使わず、`--json`の出力とstderrをPueueのjobログに残す。Pueueはstdinを開いたままにするため、`codex exec ... </dev/null`として追加入力待ちを防ぐ。別のログファイルへ重複保存しない。
- 応答の`thread.started`に含まれるセッションIDを要約job IDと一緒に既存の実行記録へ残し、`pueue log <要約job ID>`で応答を追えるようにする。起動前に失敗してIDがなければ、その失敗を記録する。
- 非対話の要約jobも、要約スキルに従って重要な比較結論をknowledgeへ自動記録し、保存した短い本文・保存先を最終応答に残して終了する。未検証アイデアなど確認が必要な内容は未保存の具体案として応答に残す。ジョブログへの出力をユーザーへの通知済みと扱わない。後の対話で結果確認を依頼されたら、保存した知見を確認・訂正できるように示し、未保存の案があれば再提示する。アイデアなどの確認待ちだけを理由に要約jobを失敗・待機扱いにしない。
- CLIで探す場合は`codex resume --all --include-non-interactive`を使う。通常の一覧では非対話セッションや別directoryのセッションが隠れる。IDが分かれば`codex resume <セッションID>`で開く。
- 対象trial・fold・採用結果のjob／run IDと成果物の集合と後続job IDを既存の実行記録へ残す。失敗trial・不足foldがあれば、その欠落を集計に残す。個別サマリと全体の系統図・一覧表、重要な比較結論がある場合はknowledgeの記録を確認して完了とする。要約jobから新たな実験を投入しない。

依頼なしにrunをstart/stopせず、outputやartifactをdeleteしない。破壊的操作が必要なら対象と影響を示して承認を求める。
