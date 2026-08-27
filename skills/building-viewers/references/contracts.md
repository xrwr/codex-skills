# Viewer Contracts

## 目的

画面実装前に、対象データからViewerの境界を決める。以下を機械的な固定schemaとしてコピーせず、実データに合わせて具体化する。

## 最初に確認するもの

- データroot、output root、文書rootと実在するfile
- itemの階層、stable ID、join key、split、provenance
- 一覧件数、最大item size、更新頻度、生成途中の状態
- 既存のAPI、frontend、router、state管理、theme、test
- 主表示に必要なraw dataと、一覧だけで必要なmetadata
- 読み取り専用であること。書き込み要求がある場合は別設計に分ける

依頼文と現物が一致しない場合は、存在しない形式を推測実装しない。実在する一件を表示する縦切りを優先し、未確認形式は未確認と報告する。

## Data flow

```text
repository data/artifacts
  -> catalog adapter
  -> summary / detail / issue models
  -> FastAPI read-only endpoints
  -> frontend adapter
  -> selector / domain viewport / inspector
```

domain file形式をReact componentへ直接漏らさない。catalog adapterが検証と正規化を担当し、frontendは表示契約だけを読む。

## Catalog contract

### Summary

一覧に必要な軽量情報だけを返す。

- opaqueな`id`
- 利用者向けのnameとkind
- statusと一覧用の小さなmetadata
- detailやpreviewのavailability

raw array、長文、画像bytes、filesystem pathをsummaryへ含めない。

### Detail

選択された一件だけを遅延取得する。

- summaryと同じ`id`
- provenance、metrics、annotation、表示設定
- 主表示が取得するresourceのopaque ID

大きなbinaryはJSONへ埋め込まず専用endpointで返す。要求途中で選択が変わる場合は`AbortController`またはrequest identityで古い応答を破棄する。

### Issue

一件の破損でcatalog全体を停止させない。

- itemを特定できる安全なID
- 利用者が次の操作を選べる説明
- severityまたはstage

公開responseへ絶対path、traceback、生の例外文字列を返さない。詳細logはserver側だけに置く。

## API contract

最小形は次の4 endpointとする。既存APIがあればその規約へ合わせる。

```text
GET /api/health
GET /api/items
GET /api/items/{item_id}
GET /api/issues
```

- 一覧とartifact更新が必要なら明示的refreshを追加する。
- read-only Viewerの通常操作はGET/HEADだけにする。
- 任意pathをqueryやpath parameterとして受け取らない。
- server-side catalogがopaque IDを検証済みpathへ解決する。
- root外参照、`..`、absolute path、symlink escapeを拒否する。
- 404は未知ID、422は既知itemのdecode/validation失敗、503はcatalog全体を利用できない状態に使う。
- 更新される一覧には`Cache-Control: no-store`、immutableに近いresourceには適切なprivate cacheを使う。

## UI contract

### Desktop

- 左: selector rail。検索、filter、statusを置く。
- 中央: domain viewport。最も大きな面積を与える。
- 右: inspector。選択中itemのmetadataと詳細を置く。
- railを閉じてもtoggle位置と主表示の基準位置を安定させる。
- grid childへ`min-width: 0`を指定し、page全体の横overflowを防ぐ。

三領域すべてが必要とは限らない。情報量が少なければright inspectorを折りたたみ要素へ下げる。

### Mobile

- desktop列を細く並べない。
- domain viewportを常時の主表示にする。
- selectorをstickyな選択バーとbottom sheetまたはdrawerへ移す。
- inspectorを折りたたみsectionまたはsheetへ移す。
- sheetのEscape、backdrop、close button、scroll lock、focus移動と復帰を実装する。
- 360px級の幅とtouch targetを検証する。

## State contract

共有・再現に必要な状態はURL queryへ置く。

- 選択item、run、split、label、view modeなど
- 不正または消えたIDは利用可能な安全なfallbackへ戻す
- 選択変更時はback buttonの意味に応じて`pushState`と`replaceState`を選ぶ

端末固有の状態だけを`localStorage`へ置く。

- sidebar開閉、scroll位置、最後の補助panelなど
- storageが拒否されてもViewer本体を動かす

## Explicit states

次を空配列や同じspinnerへ潰さない。

- initial loading
- stale dataを保持したrefreshing
- empty catalog
- filter resultが0件
- API connection error
- item detail error
- partial catalog with issues
- unsupported artifact
- generating / incomplete / complete

statusは実artifactから判定し、directoryや設定fileの存在だけでcompleteにしない。

## Vertical slice

最初の受け入れ条件は、一つの実itemについて以下が通ることとする。

1. catalogが検出する。
2. summary一覧に出る。
3. URLから選択を復元できる。
4. detailを遅延取得する。
5. domain viewportが実内容を描画する。
6. inspectorがprovenanceを表示する。
7. desktopとmobileから到達できる。
8. 壊れた隣接itemがあっても表示を継続する。

## Completion evidence

- backend contract test
- frontend component、state、responsive test
- lint、typecheck、production build
- 代表・最大・壊れたitemでの確認
- 実ブラウザでURL再読込、主要操作、横overflow、console error確認
- remote経路がscopeなら、その実URLで内容まで確認
