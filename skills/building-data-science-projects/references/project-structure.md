# Project Structure

## Core Layout

GreenfieldのPython data-science projectは、必要なdirectoryだけを次のownershipへ配置する。

```text
pyproject.toml
uv.lock
src/
└── {package_name}/
scripts/
tests/
configs/
data/
outputs/
notebooks/
app/
```

すべてを先に作らない。現在のprojectでownerが存在するdirectoryだけをmaterializeする。

| Path | Owner・用途 |
|---|---|
| `src/{package_name}/` | import可能なdomain・application code |
| `scripts/` | configやCLIを解決して`src`を呼ぶ薄いentrypoint |
| `tests/` | behaviorとboundary contract |
| `configs/` | 実装が読む明示的なconfiguration |
| `data/` | source control外のinput・generated dataset artifact |
| `outputs/` | run、metric、checkpoint、figureなど再生成可能なartifact |
| `notebooks/` | review可能な探索・報告用source |
| `app/` | 実際にapplication deliveryが必要な場合だけ |

## Code and Config Boundary

`src`は通常のPython valueまたはobjectを受け取り、HydraやOmegaConfなどのconfig framework型へ依存させない。Framework固有のcompose、resolve、instantiateは薄いentrypointへ留める。

Experiment configを導入する場合は`managing-experiments`を使い、task-local config、shared component、experiment selectionのownershipを決める。このreferenceではその構造を複製しない。

## Exploratory Files

探索用notebookは、version control、diff、reviewを優先して`.py`と`# %%` cellをdefaultにする。Hosted notebook、教材、widget、既存workflowなど`.ipynb`が必要な場合は、その理由を優先する。

Notebookへ再利用するdomain logicを残さず、安定した処理は`src`へ移す。Notebookまたはscriptは公開APIを呼ぶconsumerにする。

## Data and Outputs

- Raw input、generated dataset、run outputのownerと再生成方法を分ける。
- Credential、token、private pathをtracked configへ保存しない。
- 大きなbinaryや生成物をGitへ追加する前にrepositoryのartifact contractを確認する。
- Outputはexperiment ID、attempt/run ID、resolved config、provenanceを追跡できる形にする。詳細は`managing-experiments`へ委ねる。
