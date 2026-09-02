---
name: drawing-model-architecture-diagrams
description: Use when a user explicitly asks to create, draw, or include an SVG diagram for a model architecture, neural network, tensor pipeline, or 「モデル構成」「アーキテクチャ」「処理フロー」の図解。
---

# Drawing Model Architecture Diagrams

## Overview

モデルをlayer一覧ではなく、入力から出力まで責務とtensor shapeを追えるSVGとして描く。指定がなければ意味上のまとまりを優先し、実装詳細を展開しすぎない。

## Workflow

1. 利用可能なmodel code、config、論文、説明文を確認し、確認済み事項と推定を分ける。
2. 図が答える問いを一つ決め、`input → representation → aggregation/merge → head → output`の主経路を作る。
3. 連続するlayerを責務単位へ畳む。指定がなければ一経路を概ね4〜9個の主要blockに収める。
4. 入力shapeと出力shapeは必須とし、branch前後、merge後、軸や解像度が変わる地点にもshapeを置く。
5. [svg-guidelines.md](references/svg-guidelines.md)に従ってSVGを直接作る。diagram用YAMLや汎用rendererは、反復作業が実際に発生するまで導入しない。
6. SVGを実際にrenderし、意味、shape、文字切れ、重なり、矢印、縮小時の可読性を確認する。

## Granularity

同じ責務を持つ連続処理は一つにまとめる。たとえば概要図では、内部のConv、Norm、Activation、Downsampleを列挙せず、`U-Net Encoder`を一つのblockとして扱い、必要なmulti-scale featureだけを外へ示す。

次のいずれかに当たる部分だけを一段展開する。

- その内部構造自体が質問の対象である。
- branch、merge、skip connectionを見せないとdata flowを誤解する。
- 空間、時間、depth、channel、sequenceの軸変換が説明に必要である。
- shared weightか別weightかがモデルの意味を変える。
- attention、pooling、head、lossへの接続が結論に関係する。

比較図では共通部分を畳み、差分部分だけを同じ縮尺で展開する。装飾や空き領域を埋めるためにblockを増やさない。

## Shape Contract

- `B, C, D, T, H, W, N`などの記号を図全体で統一する。
- 入力、出力、branch/merge、axis-changing operationを優先し、全layerへshapeを付けない。
- 可変長や未確定値は`N_i`、`C_i`、`D_i`などのsymbolic shapeで表す。
- rankや軸構成自体が確認できない場合はtupleを発明せず、`shape unknown`と明示する。
- 実装から確定できない数値、演算、weight共有を推測しない。必要なら主経路の外に短い未確認注記を一つ置く。
- volume slice数、2.5D入力channel数、sequence lengthなど、意味の異なる軸を一つの「枚数」にまとめない。
- concatは結合軸と和、stackは追加軸、pool/squeezeは消える軸が追えるようにする。

## Quick Reference

| 依頼 | 既定の粒度 |
|---|---|
| モデル全体を説明 | 主要な責務だけを4〜9 blockで示す |
| 特定blockを説明 | 対象だけ一段展開し、前後は畳む |
| 複数モデルを比較 | 共通部を畳み、差分だけ展開する |
| shapeが一部不明 | 数値を作らずsymbolic shapeを使う |
| codeがない | 概念図と明示し、実装固有の演算を断定しない |

## Common Mistakes

| 誤り | 修正 |
|---|---|
| module treeをそのまま全展開する | 図の問いに必要な責務へ畳む |
| 未確定事項ごとに`TBD`を置く | symbolic shapeと一つの注記へ集約する |
| shapeを全矢印へ繰り返す | 入出力と意味が変わる境界に限定する |
| branchごとに理由なく色を変える | 色は役割差が必要な場合だけ使い、textでも区別する |
| 見栄えのために演算を補う | 確認できない演算は描かない |
| SVG sourceだけ見て完了する | render結果を表示して確認する |

## Completion Check

- 入力から出力まで矢印だけで辿れる。
- 入力shapeと出力shapeがあり、重要な軸変換に矛盾がない。
- 畳んだblockと展開したblockの理由を説明できる。
- 確認済み構造と概念的・未確認の構造が混同されていない。
- SVGが編集可能で、実表示に文字切れや重なりがない。
