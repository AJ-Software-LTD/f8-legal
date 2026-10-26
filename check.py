#!/usr/bin/env python3
"""Checks each translation against English: same placeholders, links, headings, list shape and ui.json keys."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).parent / "content"
def shape(text):
    body = text.split("---", 2)[2]
    return {
        "placeholders": sorted(re.findall(r"\{\{\w+\}\}", body)),
        "urls": sorted(re.findall(r"\]\(([^)]+)\)", body)),
        "headings": sum(1 for l in body.splitlines() if l.startswith("## ")),
        "items": [len(m) for m in re.findall(r"^( *)- ", body, re.M)],
        "front": sorted(re.findall(r"^(\w+): ", text.split("---", 2)[1], re.M)),
    }
ok = True
langs = sys.argv[1:] or sorted(p.name for p in ROOT.iterdir() if p.name != "en")
en_ui = set(json.loads((ROOT / "en/ui.json").read_text()))
for lang in langs:
    for doc in ["privacy.md", "terms.md"]:
        a, b = shape((ROOT / "en" / doc).read_text()), shape((ROOT / lang / doc).read_text())
        for k in a:
            if a[k] != b[k]:
                ok = False; print(f"{lang}/{doc}: {k} differs")
    ui = json.loads((ROOT / lang / "ui.json").read_text())
    if set(ui) != en_ui or not ui["translationNote"]:
        ok = False; print(f"{lang}/ui.json: keys or translationNote wrong")
print("OK" if ok else "PROBLEMS")
