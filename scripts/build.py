"""Build the static website in dist/ from the sources in src/.

Source layout:
  src/layouts/<name>.html    page shell; placeholders {lang} {dir} {title}
                             {description} {header} {content} {footer}
  src/partials/<name>.html   shared headers and footers
  src/pages/**.html          one file per page: front matter, then the <main> element
  src/static/                copied to the output as-is (stylesheet, images)

Front matter is a block of `key: value` lines between two `---` lines. Keys:
  title, description, lang (required); header, footer, layout (default "base").

Layouts, partials and pages are indented across lines for editing. The build
joins every line break and the indentation after it, so the output pages are
single-line HTML. Never break a line inside text where a space is needed.
"""

import argparse
import re
import shutil
from pathlib import Path

RTL_LANGS = {"he", "ar"}
LINE_BREAK = re.compile(r"\n[ \t]*")
FRONT_MATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def compact(text):
    return LINE_BREAK.sub("", text.strip("\n"))


def read_page(path):
    text = path.read_text()
    match = FRONT_MATTER.match(text)
    if not match:
        raise SystemExit(f"{path}: missing front matter")
    meta = {}
    for line in match[1].splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip()
    for key in ("title", "description", "lang"):
        if key not in meta:
            raise SystemExit(f"{path}: missing '{key}' in front matter")
    return meta, text[match.end():]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", default="src")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    src, output = Path(args.src), Path(args.output)

    def part(folder, name):
        return compact((src / folder / f"{name}.html").read_text()) if name else ""

    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(src / "static", output)

    pages = sorted((src / "pages").rglob("*.html"))
    for page in pages:
        meta, content = read_page(page)
        lang = meta["lang"]
        html = part("layouts", meta.get("layout", "base")).format(
            lang=lang,
            dir="rtl" if lang in RTL_LANGS else "ltr",
            title=meta["title"],
            description=meta["description"],
            header=part("partials", meta.get("header")),
            content=compact(content),
            footer=part("partials", meta.get("footer")),
        )
        target = output / page.relative_to(src / "pages")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html)
    print(f"Built {len(pages)} pages into {output}/")


if __name__ == "__main__":
    main()
