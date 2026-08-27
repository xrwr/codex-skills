---
name: building-viewers
description: Use when a user asks to build, create, add, redesign, or extend a viewer or 「ビューア」 for data, images, time series, experiment artifacts, validation results, model outputs, or repository documents.
---

# Building Viewers

## Overview

対象リポジトリの実データと既存構成を起点に、読み取り専用Viewerを最小縦切りから作る。画面の見栄えより先に、一覧・詳細・主表示・issueの契約と完成条件を固定する。

## Workflow

1. `rg --files`、設定、artifact、既存UI/API、テスト、起動方法を調べる。依頼文と現物が違えば現物を優先し、差分を明示する。
2. 一覧の選択単位、詳細、主表示、filter、更新方法、最大規模を決める。[contracts.md](references/contracts.md)を読む。
3. 既存Viewer stackがあれば、そのnavigation、state、component、theme、testへ追加する。なければ`assets/viewer-starter/`を`scaffold_viewer.py`で展開して適応する。
4. 一つの実データについて`catalog → summary API → detail API → main viewport → inspector`をTDDで通す。複数画面や高度な描画を先に作らない。
5. 共有状態をURL、端末固有状態を`localStorage`へ置く。loading、empty、error、partial issueを別状態にする。desktopは主表示を広く取り、mobileは主表示を優先して選択UIをsheetへ移す。
6. 配信が必要なら[deployment.md](references/deployment.md)を読む。利用可能な既存経路を調べ、要求に合う最小のものだけを選ぶ。
7. unit test、contract test、lint、production buildの後、実ブラウザで実データ、再読込、URL復元、mobile、横overflow、consoleを確認する。

## Starter

新規構築時だけ次を実行する。

```bash
python <skill-dir>/scripts/scaffold_viewer.py viewer \
  --project-name "Example Viewer" \
  --package-name example_viewer
```

生成物は完成品ではない。domain catalogと中央表示を対象データへ置換し、対象リポジトリのdependency管理とrun commandへ統合する。既存targetを上書きしない。

## Quick Reference

| 状況 | 選択 |
|---|---|
| 既存React/FastAPIがある | 既存構成へ追加し、starterをコピーしない |
| Viewer stackがない | starterを展開し、最小縦切りだけ残す |
| artifactが増え続ける | refresh可能なcatalogとsummary/detail分離 |
| 一部が壊れている | 全体を止めずitem単位のissueにする |
| 別PCから見たい | 利用可能な配信能力を確認してから選ぶ |

## Common Mistakes

| 誤りやすい判断 | 修正 |
|---|---|
| データ契約より先に3ペインやchartを量産する | 一件の実データをcatalogから主表示まで通す |
| 既存Viewerにもstarterをコピーする | 既存のrouter、state、theme、testへ適応する |
| API responseへfilesystem pathや生の例外を返す | opaque IDと安全なissueへ変換する |
| desktopの3列をmobileで縮小する | 主表示を残しselectorをsheetへ移す |
| directoryやcheckpointの存在だけでrunをcompleteにする | 必要artifactを検証してstatusを決める |
| portableならcontainerやTailscaleが必須だと決める | 配信要求と利用可能な能力から最小経路を選ぶ |
| HTTP 200だけで完成とする | 実ブラウザで内容、操作、consoleを確認する |

## Red Flags

- 実データを一件も表示していない。
- 不明なjoin keyやartifact schemaを推測している。
- 既存のdirty workや別画面を壊している。
- 外部公開なのに認証・TLS・path露出を確認していない。
- 書き込み機能を依頼なく追加している。
