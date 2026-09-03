# SVG Guidelines

## Document

- rootの`<svg>`に`viewBox`を設定し、固定pixel幅だけに依存させない。
- 背景はwhiteを既定とし、図そのものの周囲だけに余白を取る。
- accessibility用の`<title>`と`<desc>`は置くが、同内容をvisible titleや説明文として重複させない。
- 外部font、CDN、JavaScriptへ依存しない単一SVGにする。実画像が必要なら埋め込む。
- operation名など通常の文字は編集可能な`<text>`として残す。
- 図全体を囲うouter panel、角丸section card、説明用cardを既定では作らない。

## Visual Grammar

少数の視覚文法を決め、同じ意味には同じclass、glyph、色、線幅を使う。

- operation: 単純な矩形。中には処理名だけを置く。
- image/volume: 最終入出力に使う、実データに近いglyph。実画像がなければ面または直方体で表す。
- tensor: rankと意味に対応する下記のglyph。shape labelは外側に置く。
- merge/aggregation: 小さな接続点、演算記号、bracketなど、operationと区別できる形にする。
- connector: 主経路は一種類。recurrent/state経路だけ必要ならaccentを一種類追加する。

凡例は、反復する色またはglyphの対応を示すことで図中のlabelを実際に減らせる場合だけ置く。単発要素の説明や補足文章には使わない。

## Branch, Merge, and Repetition

- branch pointは実際に共有されるtensorへ置き、共通operationを手前、branch固有operationを分岐後へ並べる。
- 複数tensorから一つの出力を作る箇所では、concat、add、dot product、attentionなどの演算glyphへ入力を集め、その結果から出力tensorへ接続する。
- bracketは同時に繰り返されるoperationだけを囲み、反復範囲を正確に示す。層間feedbackは一回の反復内で得られる中間tensorから次の反復の入力へ局所的に接続する。

## Shared Operations and Persistent State

- 同じoperationを独立したstreamへ適用するときは、streamごとの独立したportを持つblockか、対応するblock間のshared-weight markerでweight共有を表す。
- memory bank、index、cacheなどの永続artifactには、通常のtensorと区別できるtable、double outline、database glyphなどを一貫して使う。
- build/index laneとinference laneを整列し、両phaseの接続は永続artifactだけを介して示す。

## Layout

- 左から右を主経路、上下をbranchやscaleに使う。自然な反復軸が縦方向なら例外を許す。
- 同じchannel、location、scale、frameは同じ寸法と間隔で整列し、省略記号で中間を省く。
- 一つの図では一つのdetail regionだけを展開する。展開が主経路と競合する場合は別図にする。
- connectorは直線または直交線を使い、text、shape label、glyphを横切らせない。配置段階で交差を0にすることを目標にする。
- 矢印はblock境界や実際のtensor glyphで止める。曖昧な空間、外枠、説明cardへ接続しない。
- 各block、tensor、connectorを意味のある`<g id="...">`でまとめる。
- 同種要素にはclassと内部`<style>`を使い、個別styleの重複を避ける。
- 矢印は`<marker>`を一度定義して`marker-end`から参照する。

## Connector Geometry

- 主経路のstroke幅はblock outlineの0.6倍程度、arrowhead長はstroke幅の3〜4倍を基準にする。小さなtargetではarrowheadをtarget glyphの高さの1/3以下に収める。
- 直交connectorの最終segmentはtarget境界に垂直に入れ、arrowhead長の2倍以上の直線部分を確保する。
- connectorは一つの連続pathとして描き、marker tipをtarget境界へ合わせる。

## Tensor Glyphs

glyphは装飾ではなくtensor semanticsを表す。shapeのrankと見た目を一致させる。

| Tensor | Glyph |
|---|---|
| image / mask `(B,C,H,W)` | 一枚の画像面。batch `B`は重ね枚数として描かない |
| volume `(B,C,D,H,W)` | 奥行きを持つ直方体またはslice stack |
| spatial feature map `(B,C,H,W)` | 必要な場合だけ重ねたfeature map面 |
| multi-scale feature | scaleごとに大きさを変え、同じ列または行へ整列 |
| vector `(B,C)` | 一本のbar |
| sequence `(B,N,C)` | `N`方向に反復するtoken/barの列。spatial feature stackにしない |
| matrix / logits `(B,N,K)` | 二軸が読めるgridまたは並んだrow |
| scalar `(B,1)` | 小さな単一cellまたは値 |

同じtensor typeは図全体で同じglyphを使う。別々の出力tensorは一つの箱へまとめず、それぞれ別glyphにする。

## Final Inputs and Outputs

- 最終入力と最終出力には、利用可能なら実画像、実mask、実predictionをcropして使う。
- 実例を使えない場合も、image、volume、mask、class vectorなどの構造が分かる実データに近いglyphを描く。
- 架空の医用画像、病変、predictionを実例らしく捏造しない。抽象glyphで代替する。
- 各external input/outputのshapeを対応するglyphに隣接させ、複数の入出力を一つのshape labelへまとめない。
- 入出力名とshapeはglyphの外に置き、縮小表示でも対応関係と式を読めるsizeとcontrastにする。
- 中間featureは主題でない限りdata-likeに描き込まず、必要な境界だけ簡素なtensor glyphにする。

## Typography and Math

- 通常表示と縮小表示の両方で読めるfont sizeとcontrastを使う。
- operation名はsans-serif、shapeと数式は一貫した数式書体にする。
- 添字、上付き、分数を手作業の`<tspan>`で近似せず、利用可能ならTeXまたはMathTextでrenderする。
- path化を許すのは数式だけとする。operation名と通常labelは`<text>`のまま残す。数式をpath化する場合は元のTeXを`aria-label`または`data-tex`に保持する。
- 色がなくても意味が分かる配置とlabelにする。色は反復する役割の区別に限定する。
- gradient、shadow、立体効果は、tensorの奥行きなど意味を伝える場合を除いて使わない。

## Verification

1. XML/SVGとしてparseできることを確認する。
2. SVGをbrowserまたは利用可能なrendererで実際に表示する。
3. 全体表示と縮小表示で、文字切れ、重なり、余白過多を目視する。
4. operation block内に処理名以外がなく、visibleな補足説明やouter panelがないことを確認する。
5. 各最終入出力がdata-likeで、縮小表示でもそれぞれのshapeを読めることを確認する。
6. tensor shapeのrankとglyphを照合し、同じtensor typeが同じ表現であることを確認する。
7. inputからoutputまでaxis continuityを追い、concat、stack、pool、squeeze、reshapeでのみ軸が変化していることを確認する。
8. 矢印のsource/targetが実際のtensorまたはoperation境界で、branch/merge、skip、recurrent経路が正しいことを確認する。
9. connectorの交差、glyphとの衝突、曖昧な接続を確認し、まず配置で解消する。
10. 外部assetなしで開けること、`<title>`と`<desc>`が存在することを確認する。
