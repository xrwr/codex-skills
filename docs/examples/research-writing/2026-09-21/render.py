"""文章サンプルを、外部接続不要の一枚のHTMLへ変換する。"""

from html import escape
from pathlib import Path
import re
from urllib.parse import unquote

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parent
PAGES = [
    ("README", "はじめに"),
    ("01-report", "01　決まった項目順で読む"),
    ("02-finding", "02　発見を見出しで拾う"),
    ("03-question", "03　疑問から答えを探す"),
    ("04-small-difference", "04　差が小さいとき"),
    ("05-incomplete", "05　評価に届かないとき"),
    ("06-exploration", "06　失敗例から問いを作る"),
    ("07-synthesis", "07　複数実験をまとめる"),
    ("08-method", "08　手法を説明する"),
    ("09-index", "09　研究の現在地"),
    ("scenario", "共通設定・架空の数値"),
]


def slug(text: str) -> str:
    """日本語を保ったまま見出しの記号と空白を除く。"""
    return re.sub(r"[^\w]", "", text).lower()


def render_page(stem: str) -> str:
    """Markdownの見出しと相対リンクをHTML内の移動先に変換する。"""
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    tokens = parser.parse((ROOT / f"{stem}.md").read_text())
    sections = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            title = tokens[index + 1].content
            section_id = f"{stem}--{slug(title)}"
            token.attrSet("id", section_id)
            if token.tag == "h2":
                sections.append((section_id, title))
        for child in token.children or []:
            if child.type != "link_open":
                continue
            href = child.attrGet("href") or ""
            path, _, fragment = unquote(href).partition("#")
            if path.endswith(".md"):
                target = Path(path).stem
                child.attrSet("href", f"#{target}" + (f"--{fragment}" if fragment else ""))
            elif path == "index.html":
                child.attrSet("href", "#01-report")
    content = parser.renderer.render(tokens, parser.options, {})
    if sections:
        links = "".join(f'<a href="#{section_id}">{escape(title)}</a>' for section_id, title in sections)
        page_map = f'<nav class="page-map" aria-label="このページの内容"><span>このページ</span>{links}</nav>'
        content = content.replace("<h2 ", page_map + "<h2 ", 1)
    content = content.replace("<table>", '<div class="table-scroll" tabindex="0" role="region" aria-label="比較表"><table>')
    content = content.replace("</table>", "</table></div>")
    return f'<article id="{stem}" aria-labelledby="{stem}-label"><p id="{stem}-label" class="eyebrow">{escape(dict(PAGES)[stem])}</p>{content}<a class="back" href="#README">見本集の入口へ</a></article>'


navigation = "".join(f'<a href="#{stem}">{escape(label)}</a>' for stem, label in PAGES)
articles = "\n".join(render_page(stem) for stem, _ in PAGES)
document = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="icon" href="data:,">
<title>研究の文章を読み比べる — 9つの見本</title>
<style>
:root { color-scheme: light; --paper: #fffefa; --ink: #252d30; --muted: #566468; --line: #dce1dd; --accent: #216553; }
* { box-sizing: border-box; }
html { scroll-padding-top: 24px; }
body { margin: 0; background: #f3f4ef; color: var(--ink); font-family: -apple-system, BlinkMacSystemFont, "Noto Sans CJK JP", "Yu Gothic", sans-serif; line-height: 1.8; }
a { color: var(--accent); text-underline-offset: 4px; }
a:hover { text-decoration-thickness: 2px; }
a:focus-visible, [tabindex]:focus-visible { outline: 3px solid #c57638; outline-offset: 4px; }
.skip { position: absolute; left: 16px; top: -80px; background: white; padding: 8px; z-index: 3; }
.skip:focus { top: 8px; }
.layout { display: grid; grid-template-columns: 250px minmax(0, 860px); max-width: 1180px; margin: auto; align-items: start; }
aside { position: sticky; top: 0; padding: 40px 22px; max-height: 100vh; overflow-y: auto; }
.brand { font-size: 17px; font-weight: 750; margin: 0 0 8px; }
.aside-note { margin: 0 0 24px; font-size: 12px; color: var(--muted); line-height: 1.7; }
nav { display: grid; gap: 3px; }
nav a { padding: 7px 0; font-size: 13px; text-decoration: none; }
nav a:hover { text-decoration: underline; }
main { min-width: 0; background: var(--paper); border-left: 1px solid var(--line); border-right: 1px solid var(--line); }
article { padding: 52px 56px 64px; border-bottom: 1px solid var(--line); scroll-margin-top: 0; }
.eyebrow { margin: 0 0 10px; font-size: 12px; font-weight: 700; letter-spacing: .06em; color: var(--accent); }
h1 { font-size: clamp(24px, 2.4vw, 31px); line-height: 1.55; margin: 0 0 26px; letter-spacing: .01em; overflow-wrap: anywhere; }
h2 { font-size: 20px; line-height: 1.6; margin: 36px 0 14px; }
h3 { font-size: 17px; }
p { margin: 0 0 20px; font-size: 16px; }
li { margin: 8px 0; }
article ul, article ol { padding-left: 1.4em; margin: 16px 0 24px; }
article li { padding-left: 3px; margin: 12px 0; }
article li p { margin: 0; }
article li::marker { color: var(--accent); }
.page-map { display: flex; flex-wrap: wrap; align-items: baseline; gap: 5px 18px; padding: 14px 0; margin: 28px 0 20px; border-top: 1px solid var(--line); border-bottom: 1px solid var(--line); }
.page-map span { font-size: 12px; color: var(--muted); }
.page-map a { font-size: 12px; padding: 2px 0; text-decoration: underline; }
blockquote { margin: 0 0 28px; padding: 8px 14px; border-left: 3px solid #a9bfb4; color: var(--muted); background: #f3f6f0; }
blockquote p { font-size: 13px; margin: 0; }
.table-scroll { overflow-x: auto; max-width: 100%; margin: 24px 0; }
table { width: 100%; border-collapse: collapse; font-size: 13px; line-height: 1.7; }
th, td { text-align: left; border-bottom: 1px solid var(--line); padding: 11px 10px; vertical-align: top; min-width: 64px; }
th { background: #edf1eb; font-weight: 650; }
td:first-child, th:first-child { padding-left: 12px; }
code { font-size: .86em; background: #eef1eb; padding: 2px 4px; border-radius: 3px; overflow-wrap: anywhere; }
pre { max-width: 100%; overflow-x: auto; padding: 16px; background: #eef1eb; }
pre code { padding: 0; }
.back { display: inline-block; margin-top: 16px; font-size: 12px; color: var(--muted); }
@media (max-width: 780px) {
  .layout { display: block; }
  aside { position: static; max-height: none; padding: 24px; }
  nav { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px 16px; }
  nav a { font-size: 12px; }
  .aside-note { margin-bottom: 14px; }
  main { border: 0; }
  article { padding: 34px 22px 42px; }
  p { font-size: 15px; }
  h2 { font-size: 18px; }
  th, td { padding: 9px 7px; }
}
@media print {
  aside, .skip, .back { display: none; }
  .layout { display: block; max-width: none; }
  main { border: none; }
  article { padding: 0; break-before: page; border: none; }
  article:first-child { break-before: auto; }
  body { background: white; }
}
</style>
</head>
<body>
<a class="skip" href="#README">本文へ移動</a>
<div class="layout">
<aside>
<p class="brand">研究の文章を読み比べる</p>
<p class="aside-note">9つの見本 / 2026-09-21<br>すべて架空の実験・数値です。</p>
<nav aria-label="文章サンプル">__NAVIGATION__</nav>
</aside>
<main>__ARTICLES__</main>
</div>
</body>
</html>
""".replace("__NAVIGATION__", navigation).replace("__ARTICLES__", articles)

(ROOT / "index.html").write_text(document)
print(f"生成: {ROOT / 'index.html'}")
