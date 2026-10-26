# f/8 Portfolio: Privacy Policy and Terms of Use

The public Privacy Policy and Terms of Use for f/8 Portfolio for iPhone, iPad and Mac, in English and the 20 languages f/8 is
translated into, served by GitHub Pages at https://aj-software-ltd.github.io/f8-legal/.

- `/privacy/` and `/terms/` send each visitor to their own language.
- `/<language>/privacy/` and `/<language>/terms/` are each language's pages, for App Store Connect and the app.

## Editing

The text lives in `content/<language>/` (`privacy.md`, `terms.md`, `ui.json`). English is the original.
After changing it, update every language, then:

```sh
python3 check.py    # each translation matches English: headings, lists, links and placeholders
python3 build.py    # writes the HTML pages
```

The company name and contact address are set at the top of `build.py`.
