# Config Architecture

## Core Contract

Experiment configを、実行に必要な選択を列挙する自己完結したselection manifestとして扱う。別のexperiment configを継承しない。既存experimentは参照元にしてよいが、新experimentへ必要なselectionを展開する。

Stable/shared componentへ切り出すのは、次をすべて満たす場合だけにする。

- 対応するconcrete implementationが存在する
- 設定のownerが明確である
- 複数consumerが使う、またはtask内で安定して再利用される

実装のない将来候補を表すspeculative groupを作らない。重複だけを理由に所有境界を変えない。

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

次の`032_focal`は`031_baseline`へ動的に依存するため不可とする。

```yaml
defaults:
  - 031_baseline
  - override /loss: focal
  - _self_
```

既存component groupを明示選択し、`032_focal`だけで選択が読める形にする。

```yaml
defaults:
  - /model: encoder
  - /data: dataset_v2
  - /optimizer: adamw
  - /loss: focal
  - /trainer: standard
  - /logger: default
  - _self_

experiment_id: 032_focal
```

## Decision Steps

1. 既存experimentのresolved configと各component groupを確認する。
2. 新experimentに必要なselectionを列挙する。
3. 所有条件を満たす既存componentを選び、selectionを新configへ明示する。
4. 条件を満たさない設定はexperimentまたはtask内に置く。
5. Entrypointでconfigをresolveし、plain value/objectへ変換してdomain `src`へ渡す。可能ならdomain `src`をHydraなどの設定frameworkから独立させる。
