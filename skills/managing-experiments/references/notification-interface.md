# Optional Pueue and Discord Notification Interface

本参照はPueue＋Discord連携を選んだ環境でだけ読む。これは管理スキル本体の依存ではない。未設定ならregisterはdisabledとなり、秘密・pueue・ネットワークへアクセスせず通知を省略する。他の実行backendでは既存の実行・要約方法を使い、このadapterの未対応を実験失敗と扱わない。Tailscaleは不要。

## ホストローカル設定

`~/.config/experiment-notify/workflow.json` のregistration_enabled／sending_enabledは設定例ではfalse。backendはpueue、scopeはexplicit_registered_experiments。approved_atはそのPCの承認後の開始時刻であり、他PCからコピーしない。秘密URLも同梱skillや設定例へ含めない。

project_defaultsはrepoからコンペ表示名を補う任意の既定値で、allowlistではない。旧projects項目も互換上の表示名既定値としてだけ読める。登録時にcompetitionを明示すれば未知のコンペ／repositoryも登録できる。全pueue jobや全repositoryを走査して自動登録する機能はない。無効な設定例（`lab-notify/experiment_notifications/workflow.example.json`）には実際のpathや資格情報を入れない。

## 既存投入からの明示登録

任意連携関数（`lab-notify/experiment_notifications/integration.py`）のregister_launchを、既存台帳をstatus=queuedで保存した後、元のenqueue処理の前に呼ぶ。wrapperが持つ設定から引数を作り、返り値を台帳のnotification欄へ保存する。registeredのrun_idをsummaryへ渡す。通知登録エラーで投入済みjobを停止・再実行しない。

```python
from integration import register_launch

record["notification"] = register_launch(
    repo=ROOT, ledger_path=ledger_path, adapter="generic", task="validation",
    competition="NEW_COMP", name="001a",
    resultsfile=metrics_path,
    primary_metric="score",
    metric_definitions={"score": {"label": "F1", "precision": 4}},
    start_notice={
        "hypothesis": "事前計画で明示した短い仮説",
        "change": "今回変更して検証する点",
        "resources": {"host_alias": "ws", "device_type": "gpu",
                      "gpu_model": "RTX PRO 6000", "gpu_count": 1, "gpu_indices": [0]},
        # 下記は書式例。計画・履歴で範囲を確認できた場合だけ実値を渡す。
        "estimate": {"min_seconds": 10800, "max_seconds": 14400,
                     "scope": "through_summary", "basis_confirmed": True,
                     "basis_ref": "確認した計画・実行履歴の参照"},
    },
)
# 既存writerでrecordを保存し、元のenqueue処理を続ける。
```

このadapterを選んだwrapperだけがホストに配置済みのlab-notify/experiment_notificationsからimportする。通知なしの通常runnerへ一律にimportを追加しない。resultsfile・primary_metric・metric_definitionsは省略可能で、指標なしなら主指標を「未確認」として結論・実測時間を通知できる。確認済みの結論がない場合も「判断不能」と不足条件を示し、推測しない。

adapterは**既存台帳形式**の指定で、競技や実行backendの制限ではない。競技別の互換形式は外部adapterの実装に従う。台帳はexperiment・trialを持ち、generic形式はnotification_jobs配列のid/role/stageを読む。roleはcompute/evaluation/helper/summary。summaryは1つで、本体・評価の後続とする。通常のユーザー操作にjob ID入力を要求しない。

戻り値はregistered＋run_id、disabled、unsupported_backend、needs_review等。終了コード0だけで登録成功と扱わずstatusを保存する。現在の実験や固定source snapshotは変更しない。既存全wrapperが自動改変された状態ではない。新規投入では、その入口が登録とsummary確認の両方へ接続していることを確認する。既存wrapperの再利用でも省略しない。通知対象のretryは既存投入経路で新しいjob IDを取得して新規登録し、同じpueue IDのrestartを旧通知へ自動統合しない。

## ARC候補比較の接続と監査

ARC repositoryのenqueue_qwen38_candidate_hints.pyは、通知設定済みホストでは確定台帳をenqueue前に登録し、結果を台帳と標準出力へ残す。check_modelはhelper。新しい固定snapshotにexperiment_notification_bridge.pyを含め、summary入口から成果物確認JSONとattestへ接続する。未設定PCでは通知連携を省略する。notification.start_noticeに計画から確認した仮説・変更点・割当資源・見積もりを明示する。未確認の見積もりを推定しない。

状態確認時はrepository直下で `python3 scripts/evaluation/experiment_notification_bridge.py audit` を実行する。承認時刻後の既知投入台帳と登録・成果物確認・配送状態をread-onlyで照合し、registration_missing、summary_verification_missing、delivery_attentionを区別する。全jobの自動登録や再送はしない。needs_reviewは通知未完として報告し、実験の再投入で修復しない。

承認済みの遅延登録だけstart_suppressed=Trueを使い、遡った開始通知を抑える。既存summaryコマンドや固定snapshotは変更せず、明示対象を待つ補助finalizerが保存済み成果物のみを照合してattestできる。実際の元summary session IDを数値job IDのJSONログから抽出し、ログ本文は通知しない。

## 開始通知の契約

登録したcomputeのRunningを観測した時だけ開始を1通送る。投入・待機・helperの開始成功・評価だけのRunningは開始通知にしない。初回観測で本体が終了済みなら開始を遡って送らない。複数foldでも開始はsummary単位で1通、直接失敗が同時に確認できた場合は終端通知を優先する。60秒間隔の観測なので短時間の本体実行は開始を観測できない場合がある。

start_noticeは任意。hypothesisとchangeは承認済み計画から登録時に明示した各180文字以下の短文だけ。欠損なら省略し、ログ・command・環境変数・未知ファイルから自動生成しない。

estimateは本体の実開始から評価・要約完了までの範囲を秒で渡す。確認済み計画・類似履歴など具体的な根拠がある場合だけbasis_confirmed=true、scope=through_summary、basis_refを指定する。根拠参照はローカル台帳に保持し、通知本文へ送らない。確認できない、範囲不正、本体のみの見積もりは所要時間・終了見込みを「未定」とする。開始時刻＋範囲からJSTの年月日と時刻を計算し、日付・年を跨ぐ場合も両端の日付を表示する。

resourcesは明示された割当情報だけ。host_aliasはws等の短い英字で始まる通称（英数字・ハイフン・アンダースコア、最大32文字）で、IP・FQDN・URLは使わない。device_type=gpuでは既知のgpu_model、gpu_count、gpu_indicesだけを渡す。番号は実際の割当番号を使い、Pueue groupから推測しない。数と番号を両方指定する場合は一致させる。CPU専用ならdevice_type=cpuで「CPU実行」と表示する。不明な項目は省略し、RAM／VRAM使用量、認証情報、環境変数は渡さない。

## 指標の契約

metric_definitionsは登録時に明示する最大8項目の辞書で、keyは対象JSON内の数値へのdot区切り参照、値はlabelと任意のprecision／scale／suffix／delta_suffix。表示名は短い固定文字列であり、結果JSONやログから生成しない。主指標を指定する場合は登録項目の1つを選ぶ。

確認済みファイルから、指定キーの有限数値のみを採用する。未指定キー、文字列、bool、配列、辞書、NaN、Infinityは送らない。結果に理由・ログ・URL・資格情報らしい自由文があっても転送しない。競技別の既存metric_profile＋metric_keysは表示定義の互換用の例で、未知コンペでは独自定義または指標なしを使う。

指標を使う場合だけresultsfileを指定する。登録した実行に帰属するファイルを確認し、summary側から下記の確認記録を渡す。未知の結果JSONを自動で要約・全文送信しない。

成功本文へはprimary_metricの今回値だけを自動表示する。補助指標が結論に必要な場合だけ、次節の確認済み根拠短文へ含める。comparisonのverified=true、metric、baseline（比較元実験・条件名）、baseline_valueに加え、assessmentで評価範囲と比較条件を確認した場合だけ、基準値→今回値と差分を表示する。未確認なら比較未確認とし、別母集団や異なる指標の差を計算しない。

## 完了結論の契約

summaryのattest用確認記録にassessmentを添える。summarizing-experimentsの事前仮説・判定基準・評価妥当性・比較・不確かさの契約に従い、対象実行の計画と保存成果物を読んで明示する。数値やexit codeからの自動分類はしない。支持は目的に対応する評価で事前基準と必要な証拠が揃う場合、不支持は判定に十分な評価で事前基準を満たさない／逆方向の結果の場合。差の不確かさ、事前記録・条件の欠落、未評価は判断不能とし、効果なし・反証と混同しない。

許可フィールドは以下だけ。URL、内部絶対path、ログ、改行、メンション、コード片は短文へ入れない。

- verified: 実際に確認した場合だけtrue。
- hypothesis: 開始前の記録と照合した仮説、180文字以内。事前記録未確認なら省略し、結果から補わない。
- verdict: supported／not_supported／undetermined。表示は支持／不支持／判断不能。
- finding: 対象範囲に限定した結論、180文字以内。実行完了の説明を入れない。
- evidence: 必要な比較根拠だけ、1〜3短文・各240文字以内。比較元、条件、値、差区間などを確認して記す。
- interpretation: 必要な場合だけ短い解釈、180文字以内。未確認の原因説明を断定しない。
- limitation: 判断を左右する制約・不足条件、240文字以内。undeterminedでは必須。
- checks: hypothesis_pre_registered／criteria_checked／evaluation_scope_checked／comparison_checked／uncertainty_checkedの5つのbool。supported／not_supportedではすべてtrueが必要。trueは意味上の照合を済ませた担当者の記録で、コードが科学的妥当性を証明した意味ではない。
- source_paths: ローカルで確認した成果物1〜8件。artifactsのhash照合対象から選び、reportを含める。仮説の事前記録確認をtrueにする場合はplanも含める。既存の計画ファイルを参照し、新規の事後計画を作らない。このpath群は通知eventにも本文にも渡さない。

例えば「差の95%区間が0を跨ぐため主目的は保留」という明示結論なら、verdict=undeterminedとし、その区間・比較元をevidence、独立性等の制約をlimitationへ渡す。指標改善やsummary成功だけでsupportedを設定しない。未確認／欠落assessmentは判断不能＋不足条件へフォールバックする。根拠ファイルが変更された場合は既存の成果物確認と同様、再確認まで終端通知を保留する。

## 成果物確認

```sh
python3 <lab-notify-dir>/experiment_notifications/workflow.py attest --run-id <登録ID> --phase summary --evidence <確認記録.json>
```

確認記録はrun_id、compute/evaluationのjob_ids、checks、artifactsを持つ。checksのselected_runs/config_code_and_data/evaluation_scopeは既存証拠で意味上の対応を確認してからtrueにする。summaryではreports_saved/knowledge_contract、summary_job_id、実際のsummary_session_idも必要。artifactsはkind/path/sha256の配列で、provenance、summary時にはreport・indexを必須とする。指標ありの場合だけmetricsも必須。更新したknowledgeも根拠へ加える。

比較元・評価条件を確認できた場合だけcomparison（verified/metric/baseline/baseline_value）、複数reportがある場合だけreport.pathで確認済みreport artifactを明示する。URLは任意adapterが実本文と照合する。foldsはcompleted/total。hash一致だけで研究上の妥当性を自動証明したと扱わない。

本人による明示中止の場合だけ、実際の停止操作とは別にrecord-cancellation --run-id <登録ID> --job-id <対象ID>を使う。このコマンド自体はjobを停止しない。

## 配送と状態

標準rendererはEmbedを使わず、通常contentを1通送る。タイトルの▶️開始／✅完了／❌失敗／⏹️中止は実行状態で、仮説支持と混同しない。完了はタイトル1行と箇条書き4行（仮説・結論・主指標・所要時間）。`- **仮説**: ...` のようにラベルだけ太字、内容は同じ行、項目間に空行を入れない。比較元・基準値・差は主指標へまとめ、必要な根拠・評価制約は結論へ短く保持する。開始も同じラベル形式で仮説・変更・資源・見込みを簡潔に示す。要約だけの失敗は❌要約失敗とし、確認範囲をタイトルに残す。

許可したラベル以外のMarkdownとメンション表記をescapeし、UTF-16相当で2000文字以内を確認する。allowed_mentionsはparse/users/rolesを空、replied_user=false、TTS=false。長すぎる確認文を意味ごと切り捨てず、修正まで保留する。秘密URLはpayloadへ含めず、既存HTTPS transportとwait=trueの配送契約を維持する。表示変更だけで過去の通知を再送・編集・削除しない。

onceは1回、watchは60秒間隔で明示登録台帳だけを対象にする。statusは台帳の観測・配送状態を読む。送り先は当該ホストで設定済みのDiscord Webhookを使い、競技ごとに認証やネットワーク設定を変えない。通知障害を学習の失敗にせず、送信不明・失敗は自動再送しない。

開始と終端は別々の永続claimで重複防止し、開始通知の送信不明・失敗でも、後の成功／直接失敗／要約失敗／明示中止は終端枠で判定する。statusのstart_deliveryは開始、deliveryは終端の配送状態。既存noticesは維持し、start_noticesだけ追加する。旧台帳や既存実験を自動登録しない。

## ポータビリティ確認例

- Discord設定なし：任意連携はdisabledで終了し、通常のコマンド実行・評価・要約を続ける。
- Pueueなし／別scheduler：外部adapterのbackendを呼ばない。明示的に別backendが設定された場合もunsupported_backendを返し、勝手にPueueを導入しない。
- Tailscaleなし：処理は変わらない。接続が必要ならそのPCの既存経路を使う。
- 新コンペ・指標なし：コンペ名と実験名を明示登録し、指標ファイルを要求せず成果物確認後に完了通知する。

## 任意のAtlasレポートリンク

ホストローカルの `~/.config/experiment-notify/report-links.json` で選ぶ任意adapter。未設定・enabled=falseなら通常通知を続ける。無効な設定例（`lab-notify/experiment_notifications/report-links.example.json`）を外部adapter側で参照し、実際のbase URL・atlas.toml path・接続IPは各ホストへ置く。Atlas・Tailscaleは実験管理や要約の必須依存にしない。

既存Atlasを使うホストだけ、enabled=true、adapter=atlas、base_url（確認済みHTTPS閲覧先）、atlas_config（既存設定）を指定する。DNS補助が必要な場合だけ、既存接続先の数値IPをconnect_ipへ明示できる。TLSの証明書とホスト名検証は維持し、公開root・認証・ACLは変更しない。

完了時のsummary receiptにあるkind=reportのpath/hashが対象repository内の現在のファイルと一致し、Atlasのproject_pathも同じrepositoryである場合だけ候補にする。reportが1件ならそれを選び、複数ならreceipt.report.pathでその集合から明示する。ファイル名の類似や最近の更新だけで選ばない。Atlasのroot名とroot相対pathからID候補を作り、実GETの文書ID・root・相対path・本文hash・versionまで照合してから `?document=...` をURL encodeして返す。ローカルpath、本文、認証情報は通知へ送らない。手書きURLやaccessible_confirmedだけを根拠に採用しない。

標準の完了4項目の末尾へ 「📄 レポートを開く」というMarkdownリンク を1行だけ追加する。SUPPRESS_EMBEDS=4でURLプレビューカードも抑える。開始・失敗・中止の本文は変更しない。未設定、Atlas未導入、未登録project、文書未生成・曖昧・不一致、HTTP失敗・redirect、容量や2000文字上限の場合はリンクだけ省略し、通知本体を失敗させない。接続確認はGETだけで、タイムアウト3秒・応答上限2MiB。過去の通知をリンク追加目的で再送・編集しない。

Tailnet内URLは、そのTailnetへ接続して既存ACLで許可された端末で開く。MacとiPhoneの実機到達確認は区別して報告する。リンク追加を、新しい文書rootの公開やFunnel・権限変更の許可と扱わない。

文書限定rootではproject_pathを省略できる。この場合だけroot.pathの実pathが対象repository直下のdocsと完全一致することを帰属条件とし、同じ文書API照合を行う。Atlasの参照ファイル・project readerもdocs内に限定される。別階層・別repositoryのdocsを推測で関連付けない。outputs等の範囲外リンクや画像を開くために境界を広げない。

## ws の通知コード配置

ws では実験通知・共通Discord送信・Kaggle提出監視の正本を `~/Projects/work/lab-notify` に置く。旧 `scripts/experiment_notifications` は同じ実体への互換symlinkであり、二重編集しない。秘密・設定・通知済み状態は従来の `~/.config/experiment-notify` と `~/.local/state/experiment-notify` を保持する。提出監視は独立した任意サービスで、実験の開始・停止・提出操作を行わない。


## 共通起動チェックと明示通知skip

通知設定済みホストの通常実験は、新規jobを保留作成→台帳確定→ローカル通知登録を確認→解放の共通経路を使う。wsでは `workflow.json` の `launch_registration_required=true` により、登録失敗時は新規jobを保留のままにする。既存jobを停止・再解放しない。Discordの送達成功は起動条件にせず、外部送信障害で学習を止めない。

短いsmoke/debug等は呼出側で `--skip-notifications` を明示できる。任意の `--notification-skip-reason smoke` とともに台帳へ `notification.status=skipped`・`explicit=true` を記録し、未登録事故と区別する。時間閾値で自動除外しない。skipは実験実行の承認を代替しない。後付け登録の `start_suppressed` を通常起動で使用しない。

coreは `lab-notify/experiment_notifications/launch_guard.py`。登録ID・台帳・job集合・開始抑止なしを永続DBと照合する。解放前にclaimを残し、二重解放や解放結果不明の自動再試行を防ぐ。adapter未設定かつ必須化していないPCではdisabledを記録して通常実行でき、Discord・Pueue・Tailscaleをcoreの必須依存にしない。

保証は共通経路の新規起動内だけ。直接python/pueueや未対応launcherをOSで禁止しない。開始通知は現行60秒Running観測のため短時間実行を見逃し得る。queue全体からの自動登録・遡及通知は行わない。起動失敗後の再開は保存されたjobとclaimを確認して別途扱う。
