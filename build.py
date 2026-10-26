#!/usr/bin/env python3
"""Builds f/8 Portfolio's Privacy Policy and Terms of Use, in every language, from content/<lang>/.

Each language has privacy.md, terms.md and ui.json. Run `python3 build.py`; it writes <lang>/privacy/,
<lang>/terms/, the language-detecting /privacy/ and /terms/ pages, and the index, ready for GitHub Pages.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
BASE = "https://built-by-aj.github.io/f8-legal"
# Who f/8 is made by, and where to reach us. Filled into every language.
COMPANY = "AJ Software Ltd"
CONTACT_URL = "https://github.com/built-by-aj/f8-legal/issues"
CONTACT_TEXT = "github.com/built-by-aj/f8-legal/issues"
# English first, then the 20 languages f/8 is translated into.
LANGUAGES = ["en", "ar", "bn", "de", "es", "fr", "hi", "id", "it", "ja", "ko", "mr", "pt-BR", "ru", "ta", "te",
             "tr", "ur", "vi", "zh-Hans", "zh-Hant"]
DOCS = ["privacy", "terms"]

CSS = """
:root { color-scheme: dark light; --bg: #1c1c1e; --raised: #2a2a2d; --text: #ececec; --body: #cfcfcf;
        --muted: #9a9a9a; --line: #38383b; }
@media (prefers-color-scheme: light) {
  :root { --bg: #f2f0eb; --raised: #e4e1da; --text: #1d1d1f; --body: #3a3a3c; --muted: #6e6e73; --line: #d6d3cc; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--text);
       font: 17px/1.65 -apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, "Segoe UI", "Noto Sans", sans-serif; }
main { max-width: 720px; margin: 0 auto; padding: 56px 16px 80px; }
.brand { font-weight: 600; font-size: 15px; color: var(--muted); text-decoration: none; letter-spacing: 0.01em; }
.brand i { font-style: italic; }
h1 { font-size: clamp(30px, 5vw, 42px); line-height: 1.2; margin: 18px 0 6px; font-weight: 700; letter-spacing: -0.01em; }
h2 { font-size: 20px; margin: 40px 0 8px; font-weight: 700; }
p, li { color: var(--body); }
ul { padding-inline-start: 22px; }
li { margin: 4px 0; }
li > ul { margin: 4px 0; }
a { color: var(--text); }
strong { color: var(--text); }
.meta { color: var(--muted); font-size: 15px; margin-bottom: 28px; }
.note { background: var(--raised); border-radius: 12px; padding: 12px 16px; font-size: 15px; color: var(--body); }
nav.switch { display: flex; gap: 16px; flex-wrap: wrap; font-size: 15px; margin-top: 8px; }
nav.switch a { color: var(--muted); }
details { margin-top: 48px; border-top: 1px solid var(--line); padding-top: 20px; }
summary { cursor: pointer; color: var(--muted); font-size: 15px; }
.langs { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 6px 16px; margin-top: 12px;
         font-size: 15px; }
.langs a { color: var(--body); text-decoration: none; padding: 4px 0; }
.langs a[aria-current] { color: var(--text); font-weight: 700; }
.docs { display: flex; flex-direction: column; gap: 10px; margin-top: 24px; }
.docs a { display: block; background: var(--raised); border-radius: 12px; padding: 14px 18px; text-decoration: none;
          font-weight: 600; }
footer { border-top: 1px solid var(--line); margin-top: 40px; padding-top: 20px; color: var(--muted); font-size: 14px; }
footer a { color: var(--muted); }
"""


def inline(text: str) -> str:
    """Escapes text, then turns **bold** and [label](url) into HTML."""
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{html.escape(m[2])}">{m[1]}</a>', text)


def markdown(source: str) -> str:
    """The small part of Markdown the documents use: ## headings, paragraphs and lists nested by two spaces."""
    out, paragraph, depth = [], [], 0

    def flush():
        if paragraph:
            out.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph.clear()

    def close_lists(to: int):
        nonlocal depth
        while depth > to:
            out.append("</li></ul>")
            depth -= 1

    for line in source.splitlines():
        item = re.match(r"^( *)- (.*)$", line)
        if item:
            flush()
            level = len(item[1]) // 2 + 1
            if level > depth:
                out.append("<ul><li>" if depth == level - 1 else "")
                depth = level
            else:
                close_lists(level)
                out.append("</li><li>")
            out.append(inline(item[2]))
        elif line.startswith("## "):
            flush(); close_lists(0)
            out.append(f"<h2>{inline(line[3:])}</h2>")
        elif not line.strip():
            flush(); close_lists(0)
        else:
            close_lists(0)
            paragraph.append(line.strip())
    flush(); close_lists(0)
    return "\n".join(out)


def read(lang: str, doc: str) -> tuple[dict, str]:
    """A document's front matter and body, with the shared details filled in."""
    text = (ROOT / "content" / lang / f"{doc}.md").read_text()
    _, front, body = text.split("---", 2)
    meta = dict(line.split(": ", 1) for line in front.strip().splitlines())
    fills = {"company": COMPANY, "contact": f"[{CONTACT_TEXT}]({CONTACT_URL})",
             "privacy": f"../../{lang}/privacy/", "terms": f"../../{lang}/terms/"}
    for key, value in fills.items():
        body = body.replace("{{" + key + "}}", value)
    return meta, body


def page(lang: str, ui: dict, title: str, description: str, body: str, canonical: str) -> str:
    return f"""<!doctype html>
<html lang="{lang}" dir="{ui['dir']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<style>{CSS}</style>
</head>
<body>
<main>
{body}
<footer>© 2026 {COMPANY} · <span lang="en"><i>f</i>/8 Portfolio</span></footer>
</main>
</body>
</html>
"""


def language_list(current: str, doc: str, uis: dict) -> str:
    links = "".join(
        f'<a href="../../{l}/{doc}/" lang="{l}" hreflang="{l}"'
        + (' aria-current="page"' if l == current else "") + f">{html.escape(uis[l]['language'])}</a>"
        for l in LANGUAGES)
    return f'<details><summary>{html.escape(uis[current]["languages"])}</summary><div class="langs">{links}</div></details>'


def build():
    uis = {l: json.loads((ROOT / "content" / l / "ui.json").read_text()) for l in LANGUAGES}
    for lang in LANGUAGES:
        ui = uis[lang]
        for doc in DOCS:
            meta, body = read(lang, doc)
            other = "terms" if doc == "privacy" else "privacy"
            note = f'<p class="note">{inline(ui["translationNote"])}</p>' if ui["translationNote"] else ""
            content = f"""<a class="brand" href="../../{lang}/" lang="en"><i>f</i>/8 Portfolio</a>
<h1>{html.escape(meta['title'])}</h1>
<div class="meta">{html.escape(ui['effective'])}</div>
<nav class="switch"><a href="../../{lang}/{other}/">{html.escape(ui[other])}</a></nav>
{note}
{markdown(body)}
{language_list(lang, doc, uis)}"""
            out = ROOT / lang / doc / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page(lang, ui, meta["title"], meta["description"], content, f"{BASE}/{lang}/{doc}/"))
        # Each language's home: its two documents.
        docs = "".join(f'<a href="{d}/">{html.escape(ui[d])}</a>' for d in DOCS)
        home = f"""<a class="brand" href="../" lang="en"><i>f</i>/8 Portfolio</a>
<h1><span lang="en"><i>f</i>/8 Portfolio</span></h1>
<div class="docs">{docs}</div>"""
        (ROOT / lang).mkdir(exist_ok=True)
        (ROOT / lang / "index.html").write_text(
            page(lang, ui, "f/8 Portfolio", "f/8 Portfolio Privacy Policy and Terms of Use.", home, f"{BASE}/{lang}/"))

    # /privacy/, /terms/ and the index send each visitor to their own language, with every language listed
    # for anyone without JavaScript. These are the addresses to use when one link has to serve everyone.
    codes = json.dumps(LANGUAGES)
    for target in ["privacy", "terms", ""]:
        suffix = f"{target}/" if target else ""
        prefix = "../" if target else ""
        links = "".join(f'<a href="{prefix}{l}/{suffix}" lang="{l}" hreflang="{l}">{html.escape(uis[l]["language"])}</a>'
                        for l in LANGUAGES)
        script = f"""<script>
(function () {{
  var codes = {codes}, wanted = navigator.languages || [navigator.language || "en"];
  function match(tag) {{
    tag = tag.toLowerCase();
    if (/^zh-(hant|tw|hk|mo)/.test(tag)) return "zh-Hant";
    if (/^zh/.test(tag)) return "zh-Hans";
    if (/^pt/.test(tag)) return "pt-BR";
    for (var i = 0; i < codes.length; i++) if (codes[i].toLowerCase() === tag.split("-")[0]) return codes[i];
    return null;
  }}
  for (var i = 0; i < wanted.length; i++) {{
    var code = match(wanted[i]);
    if (code) {{ location.replace("{prefix}" + code + "/{suffix}"); return; }}
  }}
  location.replace("{prefix}en/{suffix}");
}})();
</script>"""
        title = uis["en"][target] if target else "f/8 Portfolio"
        body = f"""<a class="brand" href="{prefix or './'}" lang="en"><i>f</i>/8 Portfolio</a>
<h1>{html.escape(title)}</h1>
<p>{html.escape(uis['en']['chooseLanguage'])}</p>
<div class="langs">{links}</div>
{script}"""
        out = ROOT / target / "index.html" if target else ROOT / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page("en", uis["en"], title, "f/8 Portfolio Privacy Policy and Terms of Use.", body,
                            f"{BASE}/{suffix}"))


if __name__ == "__main__":
    build()
