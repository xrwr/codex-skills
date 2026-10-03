# Config Architecture

## Core Contract

Experiment configには、実行に必要なcomponentの選択を明示する。既存experimentを参考に、新experimentのconfigへ必要なselectionを展開する。

設定形式と配置は既存entrypointの契約にそろえる。YAMLで管理するrepositoryではexperiment configもYAMLで作成する。既存規約がなければYAMLを案として提示する。ユーザーが形式を指定した場合はその指定に従う。

同じexperiment内のtrialは、そのselectionと計画内の変更値から構成してよい。trialのたびに新しいexperiment YAMLや全設定の手書きコピーを作らない。各実行で変更値と解決後の全設定を保存し、再現時はそのsnapshotを使う。experiment間の動的な継承と、同一experiment内のtrial overrideは区別する。

Stable/shared componentへ切り出すのは、次をすべて満たす場合だけにする。

- 対応するconcrete implementationが存在する
- 設定のownerが明確である
- 複数consumerが使う、またはtask内で安定して再利用される

実装のない将来候補を表すspeculative groupを作らない。重複だけを理由に所有境界を変えない。

## Experiment Layout and Naming

既存repositoryの配置・命名・entrypointの契約を先に確認し、通常の実験追加ではそれを維持する。以下は既存規約がない場合の提案用の標準形とする。新たな階層・共有groupが必要なら、具体的な変更パスと理由を実験案に含める。

実行単位の設定を`configs/tasks/{task_name}/`、複数taskで共有する設定部品を`configs/components/`へ分離する。各taskのentry configは`config.yaml`、experiment YAMLは`configs/tasks/{task_name}/experiment/`へ置く。Taskだけが使うgeneratorなどのgroupは、そのtaskの直下へ置く。

通常のExperiment IDには3桁の連番を付け、最初のbaselineは`001_baseline`のように命名する。既存experimentを基準に派生させる場合は、`002_finetune_from_001`のように変更内容と派生元のIDを名前へ含める。名前にはベースexperimentですでに表現されている情報を繰り返さず、意味上の差分だけを短く記述する。`from_001`は比較上の系譜を表すものであり、config inheritanceを許可するものではない。

採番するかは[run lifecycle](run-lifecycle.md)のIdentityで先に判断する。新たなtrial IDは同参照の[条件IDの表記](run-lifecycle.md#条件idの表記)に従い、`001a_baseline`・`001b_lr_half`のようにexperimentの数字IDと条件の英字を組み合わせる。派生元がtrialならそのIDと実際のコード・設定・成果物への参照を記録する。既存IDは振り直さず、trial未対応のrepositoryでは設定・出力先・loggerの対応範囲を確認してから組み込む。スキルの更新だけで実装済みと扱わない。

Config groupは次のownershipと名称にそろえる。これは許可するgroupの語彙であり、該当するconcrete implementationが存在するgroupだけを作成する。空のdirectoryや将来用のgroupは作らない。

```text
configs/
├── tasks/
│   └── {task_name}/
│       ├── config.yaml
│       ├── experiment/
│       └── {task-local-group}/
└── components/
    ├── paths/
    ├── dataset/
    ├── schema/
    ├── split/
    ├── preprocessing/
    ├── augmentation/
    ├── sampling/
    ├── dataloader/
    ├── model/
    ├── loss/
    ├── decoder/
    ├── metrics/
    ├── optimizer/
    ├── scheduler/
    ├── trainer/
    ├── logger/
    ├── callbacks/
    └── hydra/
```

## Ownership

| 設定 | Owner | 配置判断 |
|---|---|---|
| Experiment selection | 個々のexperiment | experiment configへ明示する |
| Stable shared component | 対応するimplementation | 複数consumerがある場合に共有する |
| Task-local component | 対応するtask | 安定したtask-local再利用に留める |
| Dataset artifact | artifact contract | path、schema、split、versionを保持する |
| Generator recipe | generator implementation | generation parameter、seedなどを保持する |

Dataset artifactとgenerator recipeを分離する。生成方法を変えず既存artifactを読むtaskをgeneratorへ依存させない。

## Experiment Inheritance

次の`032_focal_from_031`は`031_baseline`へ動的に依存するため不可とする。

```yaml
defaults:
  - 031_baseline
  - override /loss: focal
  - _self_
```

既存component groupを明示選択し、`032_focal_from_031`だけで選択が読める形にする。

```yaml
defaults:
  - /components/model@task.model: encoder
  - /components/dataset@task.dataset: dataset_v2
  - /components/optimizer@task.optimizer: adamw
  - /components/loss@task.loss: focal
  - /components/trainer@task.trainer: standard
  - /components/logger@task.logger: default
  - _self_

experiment_id: 032_focal_from_031
```

## Decision Steps

1. 基準experiment・trialのコード、resolved config、入力・評価条件と各component groupを確認する。
2. trial追加なら、計画内の変更値を既存のoverride・探索記録へ保存する。新experimentなら、必要なselectionを列挙する。
3. 新experimentでは所有条件を満たす既存componentを選び、selectionを新configへ明示する。
4. 条件を満たさない設定はexperimentまたはtask内に置く。
5. Entrypointでconfigをresolveして全設定を保存し、plain value/objectへ変換してdomain `src`へ渡す。可能ならdomain `src`をHydraなどの設定frameworkから独立させる。
6. 承認前の静的検証では一時領域へresolve結果を保存する。DefaultsとCLI overrideを含む解決後の設定を基準と比較し、差分が計画した変更点と一致すること、および出力先を確認して実験案へ添える。
