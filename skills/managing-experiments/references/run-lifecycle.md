# Run Lifecycle

## Identity

採番・実験と条件の区別・承認判断は[計画と承認](planning-and-approval.md#identity)を参照する。

### 条件IDの表記

[条件IDの表記](planning-and-approval.md#条件idの表記)を正本とする。

## 実行記録

trial IDはexperiment内で一意にし、各実行はjob／run IDなど既存の実行記録で特定する。並列投入では既存の採番・登録経路で重複を防ぎ、同じtrial・foldの保存先へ同時に書き込まない。各実行にexperiment・trial・fold、実際の設定、コード版、データ・評価の識別情報、コマンド、状態、指標、成果物の場所、job／run IDを記録する。修正前の結果が無効なら理由を残し、新結果と混ぜない。計算や評価の意味を変える修正は採番の判断へ戻る。

記録先は既存の台帳・CSV・DBなどを使う。軽い試行は機械的な行記録でよく、trialごとの手書きYAML・説明ファイルを要求しない。checkpoint等は、既存規約がなければ`outputs/<experiment>/<trial>/[fold-N/]`へ保存する。採用済み・比較に使った結果を再実行で失わず、実際に読み書きするpathと設定を一致させる。

仮説・承認範囲は既存の実験ドキュメントへ、実行設定は既存entrypointが読むconfigへ、実行の状態・成果物への参照は既存の実行記録へ保存する。失敗→修正→完了の履歴は同じ条件へ紐付ける。Metricやresolved configは既存writerの形式で出力する。

結果欄には確認できた事実と未確認事項を記録し、原因の推測や次の推奨を混ぜない。事後の考察はチャットで示し、実験結果に基づく重要な比較結論は、短い本文・具体的な知見保存先・根拠を追加案として提示し、その案へのユーザー承認後に記録する。既存知見の更新も変更案への承認を得る。判定・粒度と未検証アイデアの保存は要約スキルの契約に従う。

Commit IDを実験文書のヘッダーの必須項目にせず、記録のためだけのcommitも要求しない。Hydraを使う場合は各実行に対応する`.hydra/config.yaml`・`hydra.yaml`・`overrides.yaml`と既存のresolved configを再利用する。`.hydra`の保存が有効か、実行時の補間値まで確定した設定が残るかを確認し、不足分だけ既存writerで保存する。Hydraの設定記録はコードの保存ではないため、コード版は既存のコードsnapshotや、commitと未コミット差分などで識別する。必要なコード状態を確認できなければ未確認と記し、設定だけで完全な再現性を保証しない。

出力構成は[開始前の提案と確認](planning-and-approval.md#実験開始前の提案と確認)に含める。既存の出力階層を使い、学習・評価・logger・checkpointのwriterが実際に使うpathを設定と実装から確認する。Trial・foldごとの出力先を一意にし、旧実行との混在を防ぐ。補助記録は専用の保存先へ対応付ける。解決したpathを案として提示し、承認後に実行用directoryを作成する。

## W&Bを使用する場合

- 既存projectを使い、configにexperiment・trial・fold（該当時）を保存する。run名は`042c_capacity_depth4-fold0`のように、実験名と条件差を読める形にする。原則1実行を1runとし、一意なW&B run IDを台帳へ残す。run名への手動の実行回番号は要求しない。
- `group`は同一trial・同一評価計画のCV fold集合に使う（例：`042c`。同じproject内のtask間でも衝突させない）。異なるtrialをexperiment IDだけで一括groupにしない。CV以外はgroupを設定せず、チャートのrun集約も行わない。
- retryを含む全runの平均をCV結果にしない。各foldの採用結果と対応するrun IDを成果物の検証に基づいて記録し、CV集計・平均曲線にはその集合だけを使う。途中で失敗したfoldのretryによって、他foldの採用結果を消したり重複計上したりしない。fold指標の平均とOOF全体で計算した指標は区別する。
- W&Bのrun一覧の件数を減らすための概要専用run・専用ビュー・別projectへの移動は、この管理方式の要件にしない。既存runのgroupやIDを一括で書き換えない。
- 軽い探索で必要なら、上限を定めた1バッチを1runとし、trial・実行記録・条件・状態・結果をTableの行とローカル記録で対応させてもよい。複数条件を一つの学習曲線として混ぜない。
- 既存のcheckpoint再開で同じW&B runを継続する契約がある場合は、その継続と最初からのやり直しを区別し、実行履歴・再開元・stepを残す。

W&Bの[group](https://docs.wandb.ai/models/runs/grouping)と[チャートの集約](https://docs.wandb.ai/models/app/features/panels/line-plot/reference#run-grouping)は別に確認する。group属性だけでは、retryの除外や意図した集計は保証されない。

## 実行バックエンド

通常のコマンド・既存wrapper・schedulerなど、その環境で合意済みの実行方法を尊重する。Pueueがないことだけで実験を未実行扱いにしたり、導入を要求したりしない。既存backendが障害中の場合に無断で別方式へ切り替えない。queueがない環境ではprocess終了と保存済み成果物から状態を確認し、job IDがない場合は既存run ID・実行記録で識別する。

## GPU Resource Contract

GPUの台数・model・VRAM・稼働状況を確認し、既存backendの資源予約・相互排他・device bindingを使う。複数GPUがあることだけを理由にDDP、DataParallel、model sharding、1実行での複数GPU利用を選ばない。既定は独立した1-GPU実行とし、既存scheduler／runnerで重複割当を防ぐ。複数GPU利用が明示された場合だけ対応状況を別途確認する。

割当GPU・host・launch commandと利用可能なprocess／job／run IDを記録する。同じ条件を別GPUでretryするときもexperiment・trial・foldを維持し、旧結果を混ぜない。Pueueを使う環境のgroup・parallel設定は[任意adapter](execution-adapters.md#pueueを使う場合)を参照する。

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

投入時のsummary登録・完了確認・通知は[終了処理](completion-and-notification.md)を参照する。

依頼なしにrunをstart/stopせず、outputやartifactをdeleteしない。破壊的操作が必要なら対象と影響を示して承認を求める。
