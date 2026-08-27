# Building Viewers Skill 設計

## 目的

「ビューア」「viewer」の作成・追加・刷新を求められたときに発火し、対象リポジトリの実データと既存構成を確認したうえで、読み取り専用のブラウザViewerを小さな縦切りから構築する配布可能なCodex skillを作る。

## 境界

- React、TypeScript、FastAPIを新規構築時の標準starterとする。
- 既存UI/API stackがある場合はstarterをコピーせず、既存構成を優先する。
- Data、Validation、artifact、画像、時系列、文書などの閲覧を対象とする。
- annotation、review、ROIなどの書き込み機能は対象外とする。
- 特定プロジェクト、利用者、PC、絶対path、port、hostnameへ依存しない。

## Core workflow

1. 対象リポジトリ、実データ、artifact、既存viewer、テスト、起動方法を確認する。
2. 一覧、詳細、主表示、issueの入出力契約を決める。
3. 既存stackへの追加とstarter利用を選択する。
4. 一つの実データが一覧から詳細・主表示まで到達する縦切りをTDDで作る。
5. URL状態、端末状態、loading、empty、error、partial issueを分離する。
6. desktopとmobileを検証する。
7. 配信方法は環境と要求から選び、Tailscaleやcontainerを必須化しない。
8. 実ブラウザで表示内容、操作、console、overflowを確認する。

## Starter contract

starterは、opaque IDを用いたsummary/detail API、壊れた項目の隔離、遅延detail取得、URL復元、折りたたみsidebar、mobile bottom sheet、Inspector、loading/empty/errorを備える。中央表示はdomain固有の実装へ置換できる薄い境界とする。

## 配布

公開可能な`codex-skills` repositoryの`skills/building-viewers`を配布単位とし、MIT Licenseを付与する。`~/.codex/skills`はinstall先であって正本ではない。GitHub上のskill pathからinstallできる構成にする。

## 検証

- skillなし／ありの同一シナリオ比較
- package contract test
- scaffoldの非破壊性とplaceholder置換
- FastAPI contract test
- React component、URL state、responsive CSS test
- frontend lint、typecheck、production build
- skill validator
- starterを一時directoryへ展開するsmoke test
