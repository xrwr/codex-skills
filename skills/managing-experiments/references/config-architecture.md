# Config Architecture

## Core Contract

Experiment configを、実行に必要な選択を列挙する自己完結したselection manifestとして扱う。別のexperiment configを継承しない。既存experimentは参照元にしてよいが、新experimentへ必要なselectionを展開する。

Stable/shared componentへ切り出すのは、次をすべて満たす場合だけにする。

- 対応するconcrete implementationが存在する
- 設定のownerが明確である
- 複数consumerが使う、またはtask内で安定して再利用される

実装のない将来候補を表すspeculative groupを作らない。重複だけを理由に所有境界を変えない。

## Experiment Layout and Naming

実行単位の設定を`configs/tasks/{task_name}/`、複数taskで共有する設定部品を`configs/components/`へ分離する。各taskのentry configは`config.yaml`、experiment YAMLは`configs/tasks/{task_name}/experiment/`へ置く。Taskだけが使うgeneratorなどのgroupは、そのtaskの直下へ置く。

各runnable taskの最小動作確認には`000_{task_name}_smoke`を使う。通常のExperiment IDには3桁の連番を付け、最初のbaselineは`001_baseline`のように命名する。既存experimentを基準に派生させる場合は、`002_finetune_from_001`のように変更内容と派生元のIDを名前へ含める。名前にはベースexperimentですでに表現されている情報を繰り返さず、意味上の差分だけを短く記述する。`from_001`は比較上の系譜を表すものであり、config inheritanceを許可するものではない。

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

1. 既存experimentのresolved configと各component groupを確認する。
2. 新experimentに必要なselectionを列挙する。
3. 所有条件を満たす既存componentを選び、selectionを新configへ明示する。
4. 条件を満たさない設定はexperimentまたはtask内に置く。
5. Entrypointでconfigをresolveし、plain value/objectへ変換してdomain `src`へ渡す。可能ならdomain `src`をHydraなどの設定frameworkから独立させる。
