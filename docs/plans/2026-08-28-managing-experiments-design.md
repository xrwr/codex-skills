# Managing Experiments Skill 設計

## 目的

実験、run、ablation、baseline、設定、再実行、状態確認、結果管理を求められたときに発火し、設定の所有境界、実験の系譜、実行状態、検証成果物を混同せず扱う配布可能なCodex skillを作る。

## 境界

- 一般的なPython実装、データ分析、Viewer構築、モデル選択だけでは発火させない。
- 特定利用者、プロジェクト、PC、絶対path、ライブラリ、scheduler、tracking serviceを必須化しない。
- Hydra、pueue、W&B、Lightningなどは、対象repositoryですでに使われている場合だけ利用する。
- gradient accumulation、seed、評価指標の選択、通常の公平比較など、一般的なLLMが判断できる実験論は扱わない。
- userの依頼がないstart、stop、delete、submitなどの外部状態変更は行わない。

## Package

配布単位は次の4ファイルとし、初期版にscriptsやassetsは含めない。

```text
skills/managing-experiments/
├── SKILL.md
├── agents/openai.yaml
└── references/
    ├── config-architecture.md
    └── run-lifecycle.md
```

`SKILL.md`は発火条件、中核原則、短い手順、参照先だけを持つ。`config-architecture.md`は設定の所有境界を、`run-lifecycle.md`は実験の系譜と証拠に基づく状態判定を扱う。

## Configuration architecture

- experiment config同士を継承させない。既存experimentは根拠として参照しても、必要な差分と選択を新しいexperimentに明示する。
- 複数experimentやtaskで安定して共有される設定だけを共通componentへ切り出す。
- 重複があっても、対応する実装や明確な所有者が存在しないconfig groupを先回りして作らない。
- dataset artifactとgenerator recipeなど、識別対象と生成手段が異なる設定を分離する。
- 対象stackが許す場合、domain codeを設定frameworkから独立させ、entrypointでresolved configを通常の型へ変換して渡す。

## Run lifecycle

experimentは「仮説または変更、解決済み入力・設定、実行、検証成果物」の組として扱う。YAML、queue job、process終了、checkpointの存在だけでは完了としない。

状態は少なくとも`queued`、`running`、`failed`、`partial`、`verified`を区別し、job manager、log、checkpoint、metric、最終artifactなどの実在する証拠を示す。不明な状態は推測せず`unknown`とする。

再試行では、同じ仮説を継続するならexperiment IDと系譜を維持する。古い出力は混在させず、削除ではなく退役先を明示してから新しい出力を作る。意味の異なる仮説へ変わる場合だけ別experimentとして扱う。

## Skill testing

実装前に、skillなしのsubagentへ同一の圧力scenarioを与えてREDを記録する。

1. deadline下で既存experimentを複製し、共有設定の所有境界を検討しないscenario
2. queue jobが終了しcheckpointもあるが、要求された最終評価artifactがないscenario
3. OOM後の再試行で、既存出力を残したまま新しいIDまたは同じ出力先を使おうとするscenario
4. 一般的な実装依頼でskillを発火させるnegative trigger scenario

各scenarioで選択と合理化を原文のまま記録し、それに必要な最小限の規則だけをskillへ追加する。同じscenarioをskillありで再実行し、まだ残る抜け道を閉じて再検証する。

package testではfrontmatter、implicit invocation、必須4ファイル、個人・project識別情報の不在、特定toolの強制がないことを検査する。また、`controlled-comparisons.md`、gradient accumulation、一般的な比較論がskillへ混入していないことを確認する。
