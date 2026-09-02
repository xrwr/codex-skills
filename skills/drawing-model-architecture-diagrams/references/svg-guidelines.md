# SVG Guidelines

## Document

- rootの`<svg>`に`viewBox`を設定し、固定pixel幅だけに依存させない。
- 背景はwhiteを既定とし、十分な余白を取る。ユーザー指定があれば従う。
- `<title>`と`<desc>`で図の目的と主経路を説明する。
- 外部font、CDN、JavaScriptへ依存しない単一SVGにする。実画像が必要なら埋め込む。
- textをpath化せず、編集可能な`<text>`として残す。

## Structure

- 左から右を主経路、上下をbranchやscaleに使う。例外は対象の自然な方向が明確な場合だけにする。
- 各block、label、connectorを意味のある`<g id="...">`でまとめる。
- 同種のblockにはclassと内部`<style>`を使い、個別styleの重複を避ける。
- 矢印は`<marker>`を一度定義して`marker-end`から参照する。
- connectorはblock境界で止め、text、shape label、他の矢印を横切らせない。
- multi-scale featureは整列した列として置き、同じscaleの接続を同じ高さに揃える。

## Typography and Color

- 通常表示と縮小表示の両方で読めるfont sizeとcontrastを使う。
- block名、shape、補足の階層をfont sizeとweightで区別する。
- shape表記には一貫した書式を使い、必要なら`B: batch`などの短い凡例を置く。
- 色を使わなくても意味が分かるlabelと配置にする。branchごとの装飾的な色分けは避ける。
- gradient、shadow、立体効果は、意味を伝える場合を除いて使わない。

## Images and Feature Maps

- 入力画像や予測例が説明に役立つ場合だけ配置する。
- volumeやfeature stackは、少しずらした矩形と枚数・shape labelで表す。
- 実画像がないときに、もっともらしい医用画像や予測結果を捏造しない。抽象的なplaceholderを使う。
- image、feature map、blockの視覚表現を混同させない。

## Verification

1. XML/SVGとしてparseできることを確認する。
2. SVGをbrowserまたは利用可能なrendererで実際に表示する。
3. 全体表示と縮小表示で、文字切れ、重なり、余白過多を目視する。
4. 矢印の向き、接続先、branch/merge、skip connectionを主経路と照合する。
5. inputからoutputまでshapeを追い、concat、stack、pool、reshapeによる軸変化を確認する。
6. 外部assetなしで開けること、`<title>`と`<desc>`が存在することを確認する。
