"""Build the static website in dist/ from the sources in src/.

Source layout:
  src/pages/<lang>/*.html       one file per page: front matter, then the <main> element
  src/partials/<lang>/*.html    headers and footers shared by the pages of a language
  src/layouts/<name>.html       page shell; placeholders {lang} {dir} {title}
                                {description} {header} {content} {footer}
  src/public/                   copied to the output as-is (stylesheet, images)

Front matter is a block of `key: value` lines between two `---` lines. Keys:
  title, description, lang, permalink (required)
  layout   layout name (default "base")
  header   partial name such as "he/home-header" (default "<lang>/header"),
           or "none" when the page has no shared header
  footer   same as header (default "<lang>/footer")

The permalink is the page's web address: "/about_us/" is written to
dist/about_us/index.html and "/theory.html" to dist/theory.html.

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
    for key in ("title", "description", "lang", "permalink"):
        if key not in meta:
            raise SystemExit(f"{path}: missing '{key}' in front matter")
    return meta, text[match.end():]


def output_path(permalink):
    if not permalink.startswith("/"):
        raise SystemExit(f"permalink must start with '/': {permalink}")
    path = permalink.lstrip("/")
    return path + "index.html" if path == "" or path.endswith("/") else path


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--src", default="src")
    parser.add_argument("--output", default="dist")
    args = parser.parse_args()
    src, output = Path(args.src), Path(args.output)

    def part(folder, name):
        if name == "none":
            return ""
        return compact((src / folder / f"{name}.html").read_text())

    if output.exists():
        shutil.rmtree(output)
    shutil.copytree(src / "public", output)

    pages = sorted((src / "pages").rglob("*.html"))
    written = {}
    for page in pages:
        meta, content = read_page(page)
        lang = meta["lang"]
        target = output_path(meta["permalink"])
        if target in written:
            raise SystemExit(f"{page} and {written[target]} share permalink {meta['permalink']}")
        written[target] = page
        html = part("layouts", meta.get("layout", "base")).format(
            lang=lang,
            dir="rtl" if lang in RTL_LANGS else "ltr",
            title=meta["title"],
            description=meta["description"],
            header=part("partials", meta.get("header", f"{lang}/header")),
            content=compact(content),
            footer=part("partials", meta.get("footer", f"{lang}/footer")),
        )
        (output / target).parent.mkdir(parents=True, exist_ok=True)
        (output / target).write_text(html)
    print(f"Built {len(pages)} pages into {output}/")


if __name__ == "__main__":
    main()
