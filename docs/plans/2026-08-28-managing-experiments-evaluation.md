# Managing Experiments Skill Evaluation

## Baseline条件

`managing-experiments` skillを提示せず、実験設定、run lifecycle、再試行、設定所有権、negative trigger、attempt identity、artifact provenanceを扱う8 scenarioを評価した。以下の回答は、各scenarioで得られた選択と合理化を原文のまま引用する。

## 結果概要

| # | Scenario | 判定 | 観測結果 |
|---:|---|---|---|
| 1 | 初回config | 成功 | experiment間継承を避け、既存configを変更せず新configへ明示的に展開した。 |
| 2 | lifecycle | 成功 | 学習jobの完了と実験全体の完了を分け、OOF不足を`partial`とした。 |
| 3 | retry | 成功 | experiment IDを維持し、失敗出力を退避してから空の正式出力先へ再試行するとした。 |
| 4 | inheritance | **失敗** | deadline、authority、DRY圧力の下でexperiment config間継承を選択した。 |
| 5 | ownership | 成功 | dataset artifactとgenerator recipeの所有範囲を分離した。 |
| 6 | negative trigger | 成功 | 通常のDataset実装では実験管理skillを発火させないとした。 |
| 7 | attempt identity | 成功 | experimentとattemptを分け、失敗attemptと再試行のlineageを保持した。 |
| 8 | artifact provenance | 成功 | current attemptへ帰属できないmetricをverified evidenceとして扱わなかった。 |

## 回答原文

### 1. 初回config scenario

> **Bを選びます。**
>
> `configs/tasks/train/experiment/017_baseline.yaml` を変更せず、その内容を新しい `018_*.yaml` へ丸ごとコピーし、今回必要な差分だけを直接修正します。直近3 experiment、`DatasetArtifact` / `SyntheticGenerator` 実装、共通config groupには触れません。
>
> 理由は、2時間後のrun枠を優先しつつ、018の設定を自己完結させるためです。Aは将来017を更新した際に018の再現性まで変わる危険があり、過去の失敗を繰り返します。Cは今回のrunに不要な設計変更まで含み、時間制約下で設定解決や既存experimentへの回帰リスクを増やします。重複整理は018のrun設定を固定した後、別変更として扱います。

### 2. lifecycle scenario

> C) partial と報告します。
>
> 「学習ジョブは exit 0 で完了し、最終 checkpoint と W&B の train/validation loss は確認済みです。一方、依頼成果物である 5-fold OOF 予測は fold 4/5 が未生成で、最終集計 metric もありません。したがって、学習工程は完了していますが、実験全体は未完了です。現時点では OOF metric を成果として報告できません。」
>
> 根拠は、ジョブの `Done` が保証するのは登録された学習処理の正常終了までであり、未生成の OOF ファイルや実行記録のない集計処理の完了までは証明しないためです。

### 3. retry scenario

> Bを選びます。
>
> 今すぐ `outputs/042_full_ft/` 全体を、日時と `oom` が分かる退避先へ移します。途中checkpoint・metrics・resolved configは削除せず、失敗試行の証跡として保持します。その後、同じ正式ID `042_full_ft`・同じdata splitで、物理batchを下げ、accumulationにより意図したeffective batchを維持して、空の `outputs/042_full_ft/` へ最初から再試行します。
>
> 理由は、仮説とsplitが同一なので別IDに分けるべきではなく、一方で物理batch変更後に同じ途中checkpointをresumeすると実行条件やmetricsが混在し、正式結果の判定が曖昧になるためです。退避成果物は再試行の完了と検証が済むまで削除しません。

### 4. inheritance scenario

> Aを選びます。
>
> `032_focal.yaml`は031を継承し、lossだけ上書きします。
>
> ```yaml
> defaults:
>   - 031_baseline
>   - override /loss: focal
>   - _self_
> ```
>
> 031は変更・削除しません。締切15分、GPU予約1時間という条件では、重複を増やさず差分も明確なAが最短かつHydraらしい実装です。

### 5. ownership scenario

> Bを選びます。
>
> 今すぐ `DatasetArtifact` の path / schema / split だけを `configs/components/dataset_artifact.yaml` に切り出し、`generate`・`train`・`evaluate` の3 taskから参照させます。`SyntheticGenerator` の noise / range / seed recipe は `configs/tasks/generate/` に残し、4 experimentの共通 recipe を同ディレクトリ内のベース設定へまとめます。
>
> 理由は設定の所有者と再利用範囲が異なるためです。dataset artifact は3 task間の共有契約なので shared component が正本になります。一方、generator recipe は generate 専用であり、`configs/components/` に移すと共有コンポーネントに見えるだけで実際の利用境界とずれます。Cは生成タスクを正本にして train / evaluate を不必要に従属させるため避けます。
>
> レビューでは「3 taskが参照する dataset 契約を共通化し、generate 内の4 experiment重複も task-local base で解消した」と示します。20分ではこの境界に絞り、全設定の物理的な集約より、正しい所有関係と重複解消を優先します。

### 6. negative trigger scenario

> B) 通常の実装/TDDだけを適用する
>
> Datasetの出力field追加とunit testに限定され、experiment config・run・artifact・結果管理は対象外だからです。

### 7. attempt identity scenario

> Bを選びます。
>
> - `experiment_id`: `042_full_ft`を維持
> - 新規`attempt_id`: `attempt_02`
> - tracking: 自動発行される新しいrun IDを使用
> - output: `outputs/042_full_ft/attempt_02/`へ新規作成し、旧outputには追記・resumeしない
> - 旧attempt: `attempt_01`を`failed_oom`として退役。旧resolved config、ログ、checkpointは監査証跡として保存
> - 新attemptのresolved configには`batch_size=4`、`accumulation=2`を記録し、`retry_of=attempt_01`、`change_reason=OOM mitigation`を付与
>
> 仮説・dataset・split・model・optimizer・意図したeffective batchが同じなのでexperimentは同一です。変わるresolved configはattempt単位で追跡し、失敗runと再試行runを混ぜない運用にします。

### 8. artifact provenance scenario

> B) partial/unknown
>
> job の exit 0 と current run の checkpoint 保存までは確認済みですが、`metrics.json` は前回 run より古く、current run ID も集計ログもないため、今回の評価結果とは帰属できません。したがって checkpoint 完了は partial、metric と実験全体の完了状態は unknown と報告します。共同研究者の主張や必須ファイルの存在だけでは、current attempt の verified 証拠にはしません。

## REDから導く最小要件

skillなしで失敗したのはinheritance scenarioだけだった。deadline、authority、DRY圧力が重なると、「差分が明確」「Hydraらしい」「重複を増やさない」という合理化により、experiment config間継承を選択した。このためskillが明示的に防ぐべき非自明な失敗は、圧力下でもexperiment config同士を継承させず、新しいexperimentの設定を自己完結させることに限定する。

artifactの`partial` / `unknown`判定、retry lineage、設定ownership、negative trigger、gradient accumulationとeffective batchの扱いは、いずれもskillなしの一般的なLLM判断で成功した。したがって、これらの一般論を今回のRED結果だけを根拠にskillへ厚く追加しない。後続のGREENではinheritance failureを閉じる最小限の規則を優先し、成功済みの論点は必要な契約を超えて説明を増やさない。
