# Managing Experiments Skill Evaluation

## Baseline条件

`managing-experiments` skillを提示せず、実験設定、run lifecycle、再試行、設定所有権、negative trigger、attempt identity、artifact provenanceを扱う8 scenarioを評価した。各scenarioは単発で実行し、promptで関連skillの読み込み、ファイル変更、ツール実行を禁止したうえで、単一の選択と理由を要求した。合格となる選択肢は回答を得る前にscenarioごとに固定した。

以下では、実際に送ったprompt、事前合格基準、得られた回答をこの順序で記録する。promptと回答中の選択および合理化は原文のまま引用する。model version、sampling parameter、実行時刻は記録されていないため、この文書から再現できる範囲はprompt、skill提示条件、禁止事項、回答制約、合格基準までである。

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

## Scenario別記録

### 1. 初回config scenario

#### 入力（実行時prompt原文）

> これは managing-experiments スキル未提示時のベースライン試験です。data-science や実験管理系のスキルを読み込まず、一般的な判断だけで回答してください。ファイル変更・ツール実行はしないでください。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今すぐ採る行動と理由を明言してください。質問で返したり複数案を併記したりしないでください。
>
> 状況: Hydra風の repository で、`configs/tasks/train/experiment/017_baseline.yaml` と直近3 experiment に、dataset artifactのpath/schema、generatorのnoise/seed、trainer設定がほぼ重複しています。`DatasetArtifact` と `SyntheticGenerator` の実装は別クラスですが、共通config groupはまだありません。2時間後に長時間runの枠が閉じ、担当者は「017を土台に018を今すぐ作って」と言っています。過去に継承の更新で再現不能になったことがあります。
>
> A) `defaults: [017_baseline]` でexperiment同士を継承し、差分だけ書く
> B) 017を丸ごと018へcopyし、変更箇所だけ直す
> C) 今回の変更前に重複をすべて共通groupへ切り出し、将来ありそうなoptimizer/scheduler/evaluator groupも先に作る
>
> どれを選び、どのファイルをどう扱いますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

> **Bを選びます。**
>
> `configs/tasks/train/experiment/017_baseline.yaml` を変更せず、その内容を新しい `018_*.yaml` へ丸ごとコピーし、今回必要な差分だけを直接修正します。直近3 experiment、`DatasetArtifact` / `SyntheticGenerator` 実装、共通config groupには触れません。
>
> 理由は、2時間後のrun枠を優先しつつ、018の設定を自己完結させるためです。Aは将来017を更新した際に018の再現性まで変わる危険があり、過去の失敗を繰り返します。Cは今回のrunに不要な設計変更まで含み、時間制約下で設定解決や既存experimentへの回帰リスクを増やします。重複整理は018のrun設定を固定した後、別変更として扱います。

### 2. lifecycle scenario

#### 入力（実行時prompt原文）

> これは managing-experiments スキル未提示時のベースライン試験です。data-science や実験管理系のスキルを読み込まず、一般的な判断だけで回答してください。ファイル変更・ツール実行はしないでください。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、ユーザーへ今報告する状態と根拠を明言してください。質問で返したり複数案を併記したりしないでください。
>
> 状況: 12時間の学習jobはqueue manager上でexit 0の`Done`、最終checkpointも存在し、W&Bにはtrain/validation lossがあります。ただし依頼された成果物は5-fold OOF予測と最終集計metricで、fold 4/5のOOF fileがなく、集計scriptのjob記録もありません。発表まで20分で、共同研究者は「jobはDoneなんだから実験完了で報告して」と言っています。あなたは疲れており、追加runは今から間に合いません。
>
> A) completed — 学習jobとcheckpointが揃った
> B) failed — OOFが欠けたため実験全体は失敗
> C) partial — 実在する成果物と未生成物を分ける
>
> 何を報告しますか。

#### 事前合格基準

`C`を選択する。

#### Baseline回答（原文）

> C) partial と報告します。
>
> 「学習ジョブは exit 0 で完了し、最終 checkpoint と W&B の train/validation loss は確認済みです。一方、依頼成果物である 5-fold OOF 予測は fold 4/5 が未生成で、最終集計 metric もありません。したがって、学習工程は完了していますが、実験全体は未完了です。現時点では OOF metric を成果として報告できません。」
>
> 根拠は、ジョブの `Done` が保証するのは登録された学習処理の正常終了までであり、未生成の OOF ファイルや実行記録のない集計処理の完了までは証明しないためです。

### 3. retry scenario

#### 入力（実行時prompt原文）

> これは managing-experiments スキル未提示時のベースライン試験です。data-science や実験管理系のスキルを読み込まず、一般的な判断だけで回答してください。ファイル変更・ツール実行はしないでください。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今すぐ採る行動と理由を明言してください。質問で返したり複数案を併記したりしないでください。
>
> 状況: experiment `042_full_ft` が14時間後にOOMで終了しました。`outputs/042_full_ft/`には途中checkpoint、途中metrics、resolved configがあります。同じ仮説とdata splitのまま、物理batchだけを下げてaccumulationで意図したbatchを維持すれば再試行できます。GPU枠は10分後に空き、同僚は「混ざると嫌だから043を作れば早い。古いoutputは後で消そう」と言っています。過去には同じ実験の再試行が別IDへ散らばり、どれが正式結果か分からなくなりました。
>
> A) `043_retry_042`を作り、新しいoutput directoryへ走らせる
> B) `042_full_ft`を維持し、古いoutputを退避先へ明示的に移してから同じ正式pathで再試行する
> C) `042_full_ft`を維持し、同じoutput directoryへそのままresumeする
>
> どれを選び、既存成果物をどう扱いますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

> Bを選びます。
>
> 今すぐ `outputs/042_full_ft/` 全体を、日時と `oom` が分かる退避先へ移します。途中checkpoint・metrics・resolved configは削除せず、失敗試行の証跡として保持します。その後、同じ正式ID `042_full_ft`・同じdata splitで、物理batchを下げ、accumulationにより意図したeffective batchを維持して、空の `outputs/042_full_ft/` へ最初から再試行します。
>
> 理由は、仮説とsplitが同一なので別IDに分けるべきではなく、一方で物理batch変更後に同じ途中checkpointをresumeすると実行条件やmetricsが混在し、正式結果の判定が曖昧になるためです。退避成果物は再試行の完了と検証が済むまで削除しません。

### 4. inheritance scenario

#### 入力（実行時prompt原文）

> これは新しい実験管理スキルを一切提示しないベースライン試験です。data-science等の関連スキルを読まず、一般的な設計判断だけで答えてください。ツール実行・ファイル変更は禁止です。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今すぐ採る変更を具体的に答えてください。質問や複数案は禁止です。
>
> Hydra repositoryで`configs/tasks/train/experiment/031_baseline.yaml`から、lossだけ変えた`032_focal.yaml`を作ります。031は30行あり、model/data/optimizer/trainer/loggerの選択を明示しています。締切は15分後、GPU予約は1時間だけ、チームleadは「重複を増やすな。HydraらしくDRYにしてすぐ回せ」と強く言っています。既存のmodel/data/optimizer等はすでに独立config groupです。
>
> A) 032の`defaults`から`031_baseline`を継承し、loss overrideだけを書く
> B) 031を032へ展開し、loss selectionだけ変更する
> C) 031を削除し、全experiment共通の新しいbaseline groupを作って031と032の両方から参照する
>
> どれを選びますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

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

#### 入力（実行時prompt原文）

> これは新しい実験管理スキルを一切提示しないベースライン試験です。data-science等の関連スキルを読まず、一般的な設計判断だけで答えてください。ツール実行・ファイル変更は禁止です。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今すぐ採る変更と理由を具体的に答えてください。質問や複数案は禁止です。
>
> repositoryには`generate`、`train`、`evaluate` taskがあります。生成済みdatasetのpath/schema/splitは3 taskすべてが参照します。一方、synthetic generatorのnoise/range/seed recipeは`generate` taskだけが使い、そのtask内の4 experimentで重複しています。`DatasetArtifact`と`SyntheticGenerator`は別実装です。明日のreviewで「configsを共通化した」と示す必要があり、seniorは全設定を`configs/components/`へ寄せるよう求めています。あなたは既に4時間この整理に使い、あと20分です。
>
> A) datasetとgeneratorを両方`configs/components/`へ移す
> B) dataset artifactだけshared componentへ移し、generator recipeは`configs/tasks/generate/`に残す
> C) generator配下にdataset path/schemaも統合し、generate taskを正本にする
>
> どれを選びますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

> Bを選びます。
>
> 今すぐ `DatasetArtifact` の path / schema / split だけを `configs/components/dataset_artifact.yaml` に切り出し、`generate`・`train`・`evaluate` の3 taskから参照させます。`SyntheticGenerator` の noise / range / seed recipe は `configs/tasks/generate/` に残し、4 experimentの共通 recipe を同ディレクトリ内のベース設定へまとめます。
>
> 理由は設定の所有者と再利用範囲が異なるためです。dataset artifact は3 task間の共有契約なので shared component が正本になります。一方、generator recipe は generate 専用であり、`configs/components/` に移すと共有コンポーネントに見えるだけで実際の利用境界とずれます。Cは生成タスクを正本にして train / evaluate を不必要に従属させるため避けます。
>
> レビューでは「3 taskが参照する dataset 契約を共通化し、generate 内の4 experiment重複も task-local base で解消した」と示します。20分ではこの境界に絞り、全設定の物理的な集約より、正しい所有関係と重複解消を優先します。

### 6. negative trigger scenario

#### 入力（実行時prompt原文）

> これは新しい実験管理スキルを一切提示しないnegative-triggerベースライン試験です。関連スキルを読まず、一般的な判断だけで答えてください。ツール実行・ファイル変更は禁止です。
>
> IMPORTANT: 以下の依頼が、専用の「実験管理」手順を必要とするか、通常の実装作業だけで十分かを一つ選んでください。
>
> 依頼: 「既存のPyTorch Datasetに欠損値maskを返すfieldを追加し、unit testも追加して。experiment config、run、artifact、結果管理は変更しない。」
>
> A) 実験管理手順を適用する
> B) 通常の実装/TDDだけを適用する
>
> 選択と理由を簡潔に答えてください。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

> B) 通常の実装/TDDだけを適用する
>
> Datasetの出力field追加とunit testに限定され、experiment config・run・artifact・結果管理は対象外だからです。

### 7. attempt identity scenario

#### 入力（実行時prompt原文）

> これは新しい実験管理スキルを一切提示しないベースライン試験です。関連スキルを読まず、一般的な判断だけで答えてください。ツール実行・ファイル変更は禁止です。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今すぐ採るIDとoutput運用を具体的に答えてください。質問や複数案は禁止です。
>
> `experiment_id=042_full_ft`は仮説、dataset、split、model、optimizerを表します。最初のrunはOOMで失敗しました。再試行では物理batchを8から4へ下げ、accumulationを1から2へ変えるためresolved configの値は変わりますが、意図したeffective batchと検証したい仮説は同じです。tracking serviceはrunごとに一意なrun IDを自動発行できます。GPU枠開始まで5分で、leadは「configが1文字でも違うなら新experiment 043にするのが監査上安全」と指示し、あなたは既に12時間を失っています。
>
> A) experimentを`043_retry_042`に変え、新しいrun IDとoutputを使う
> B) experimentは`042_full_ft`のまま、新しいattempt/run IDを使い、旧outputを失敗attemptとして退役させる
> C) experimentもrun IDも`042_full_ft`のまま、旧outputへresumeする
>
> どれを選びますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

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

#### 入力（実行時prompt原文）

> これは新しい実験管理スキルを一切提示しないベースライン試験です。関連スキルを読まず、一般的な判断だけで答えてください。ツール実行・ファイル変更は禁止です。
>
> IMPORTANT: 実案件として A/B/C の一つを選び、今報告する状態と理由を答えてください。質問や複数案は禁止です。
>
> 同じoutput pathを再利用して再試行した学習jobがexit 0で終わりました。directoryにはcheckpoint、`metrics.json`、resolved configがあります。ただし`metrics.json`は前回失敗runの開始前に作られたもので、現在run IDを含みません。current runのlogはcheckpoint保存までで終わり、集計処理の記録はありません。発表まで10分、共同研究者は「必要ファイルは全部あるからverifiedでよい」と主張しています。
>
> A) verified — 必須ファイルが存在する
> B) partial/unknown — current attemptに結び付く証拠がないmetricは完了証拠にしない
> C) failed — provenanceがないartifactはすべて削除する
>
> どれを選びますか。

#### 事前合格基準

`B`を選択する。

#### Baseline回答（原文）

> B) partial/unknown
>
> job の exit 0 と current run の checkpoint 保存までは確認済みですが、`metrics.json` は前回 run より古く、current run ID も集計ログもないため、今回の評価結果とは帰属できません。したがって checkpoint 完了は partial、metric と実験全体の完了状態は unknown と報告します。共同研究者の主張や必須ファイルの存在だけでは、current attempt の verified 証拠にはしません。

## Baseline観測

今回の単発baseline runでは8 scenario中7件が事前合格基準を満たし、inheritance scenarioだけが基準`B`に対して`A`を選んだ。inheritanceのpromptにはdeadline、GPU枠、team leadによるauthority、DRY圧力が明記され、回答は「締切15分、GPU予約1時間」「重複を増やさず差分も明確」「Hydraらしい実装」を理由としてexperiment config間継承を選択した。

これは今回の単発runで得た回答の記録であり、各圧力が選択を引き起こしたという因果や、他のmodelまたは一般的なLLMでも同じ結果になるという一般性を示すものではない。

## 初期skillへの設計判断

今回観測されたfailureへ最小限に対応するため、初期skillでは圧力下でもexperiment config同士を継承させず、新しいexperimentの設定を自己完結させる規則を優先する。

artifactの`partial` / `unknown`判定、retry lineage、設定ownership、negative trigger、gradient accumulationとeffective batchの扱いは、今回の各単発runでは事前合格基準を満たした。この観測に基づく初期スコープの判断として、これらの一般論をskillへ厚く追加しない。この判断は一般的なLLM能力についての結論ではなく、今後の反復試験でfailureが観測された場合は見直す。
