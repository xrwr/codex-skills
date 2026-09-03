---
name: drawing-model-architecture-diagrams
description: Use when a user explicitly asks to create, draw, or include an SVG diagram for a model architecture, neural network, tensor pipeline, or 「モデル構成」「アーキテクチャ」「処理フロー」の図解。
---

# Drawing Model Architecture Diagrams

## Overview

モデルをlayer一覧や説明カードではなく、少数の視覚文法でdata flowを読めるSVGとして描く。少ない箱を目標にせず、同じ意味を同じglyph、整列、色、線で反復する。

## Workflow

1. model code、config、論文、説明文、利用可能な実画像を確認し、確認済み事項と推定を分ける。
2. 図が答える問いを一つ決め、`input → representation → aggregation/merge → head → output`の主経路を作る。
3. 図全体では一つの抽象度を支配的にし、内部を見せる箇所は一箇所だけ選ぶ。詳細が大きければoverviewとdetailを別図にする。
4. operation blockには処理名だけを書く。shapeはblockの外へ置き、block内や図中に補足説明を置かない。
5. 入力shapeと出力shapeは必須とし、各最終入力と各最終出力へ必ず個別に表示する。中間tensorのshapeはbranch/merge、axis変更、または問いに必要な境界だけに置く。
6. [svg-guidelines.md](references/svg-guidelines.md)に従ってSVGを直接作る。diagram用YAMLや汎用rendererは、同じ生成処理の反復が確認されるまで導入しない。
7. SVGを実際にrenderし、意味、shape、glyph、文字切れ、重なり、矢印、縮小時の可読性を確認する。

## Abstraction and Repetition

同じ責務を持つ連続処理は一つにまとめる。たとえば概要図では、内部のConv、Norm、Activation、Downsampleを列挙せず、`U-Net Encoder`を一つのblockとして扱う。

総要素数を上限で縛らない。制限するのは視覚文法の種類と同時に見せる抽象度である。channel、location、scale、frameなどの反復は、同じglyphと間隔で整列し、省略記号で圧縮する。各要素を別種のcardにしない。

次のいずれかに当たる部分だけを一段展開する。

- その内部構造自体が質問の対象である。
- branch、merge、skip connectionを見せないとdata flowを誤解する。
- 空間、時間、depth、channel、sequenceの軸変換が説明に必要である。
- shared weightか別weightかがモデルの意味を変える。
- attention、pooling、head、lossへの接続が結論に関係する。

比較図では共通部分を畳み、差分だけを同じ縮尺で展開する。入力、処理、tensor、集約点、出力という小さな語彙を使い回し、装飾や空き領域を埋めるために種類を増やさない。

## Visible Content Contract

- 最終入力と最終出力は、利用可能なら実データの画像、mask、volume、predictionに近いglyphで示す。実例がなければ構造だけ正しい抽象glyphを使い、もっともらしい画像を捏造しない。
- 中間tensorは、flowやrankを理解するために必要なものだけglyph化する。全中間出力を列挙しない。
- operation blockには処理名だけを1〜2行で置く。式、shape、注、補足、箇条書きを詰め込まない。
- tensor名、shape、入力名、出力名はblockの外に置く。
- visible title、subtitle、問い、要点一覧、脚注、outer panel、section cardは、ユーザーが明示的に求めない限り置かない。
- 凡例は、反復する色またはglyphの対応を短く置くことで重複labelを減らせる場合だけ使う。

## Shape Contract

- `B, C, D, T, H, W, N`などの記号を図全体で統一する。
- 各最終入力と各最終出力のshapeを必ず個別に表示し、rankが不明でも省略せず`shape unknown`とする。中間tensorは意味が変わる境界に限定する。
- shapeは必ずtensor/image glyphの外側に置き、operation blockの中には入れない。
- 可変長や未確定値は`N_i`、`C_i`、`D_i`などのsymbolic shapeで表す。
- rankや軸構成自体が確認できない場合はtupleを発明しない。中間ではlabel自体を省けるが、最終入出力には`shape unknown`を置く。
- axis continuityを追跡する。`B`、`N`、`C`などの軸を消す場合は、pool、squeeze、selection、reshapeなど対応するoperationを明示する。
- volume slice数、2.5D入力channel数、sequence lengthなど、意味の異なる軸を一つの「枚数」にまとめない。
- concatは結合軸と和、stackは追加軸、pool/squeezeは消える軸が追えるようにする。
- 実装から確定できない数値、演算、weight共有を推測しない。未確認事項の説明は図外の返答に書き、図中の注記にしない。

## Connector Contract

- 矢印は実際に渡されるtensor glyphまたはoperation境界から出し、消費する正確な対象へ接続する。
- recurrent stateやskip connection以外では矢印のstyleを増やさない。状態経路にaccent色を使う場合も一種類に限定する。
- branchとmergeは配置で読めるようにし、connectorの交差を避ける。交差が残るなら配置変更または別図化を優先する。

## Quick Reference

| 状況 | 既定の表現 |
|---|---|
| モデル全体 | 責務単位の主経路。一つの重要領域だけ展開 |
| channel/location/scaleの反復 | 同一glyphを整列し、省略記号で圧縮 |
| 中間feature | 必要な境界だけ。全中間出力は書かない |
| 最終入出力 | shapeに加え、実データに近いimage/volume/output glyph |
| 特定moduleの詳細 | 前後を畳み、対象を別図または一箇所だけ展開 |
| shapeが一部不明 | 中間labelは省略。省略不能なら`shape unknown` |

## Subtraction Pass

完成前に各要素を一つずつ消した場合を考える。flow、rank、問いへの答えが変わらなければ削除する。説明文が必要になった場合は、文章を箱へ足さず、glyph、配置、分図で解決する。

## Completion Check

- 入力から出力まで矢印だけで辿れる。
- 各最終入力と各最終出力がdata-likeなglyphで識別でき、それぞれのshapeが隣接している。
- operation blockの中が処理名だけである。
- 中間tensorを必要な境界だけに絞り、同種の反復を同じ視覚文法で描いている。
- shapeのrankとglyphが一致し、重要な軸変換とaxis continuityに矛盾がない。
- 畳んだ領域と一箇所だけ展開した領域の理由を説明できる。
- 確認済み構造と概念的・未確認の構造が混同されていない。
- SVGが編集可能で、実表示に文字切れ、重なり、不要な交差がない。
