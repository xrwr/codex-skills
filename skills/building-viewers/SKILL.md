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
