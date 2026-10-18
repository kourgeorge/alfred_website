"""Prepare the recovered static site for a GitHub Pages base path."""

import argparse
import re
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-path", default="/alfred_website/")
    parser.add_argument("--output", default="_site")
    args = parser.parse_args()
    base = "/" + args.base_path.strip("/") + "/"
    if base == "//":
        base = "/"
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)
    shutil.copytree("dist", output, dirs_exist_ok=True)
    # Also covers script-assigned src values in the recovered HTML.
    root_url = re.compile(r'''((?:href|src|action)\s*=\s*["'])/(?!/)''', re.I)
    for page in output.rglob("*.html"):
        page.write_text(root_url.sub(lambda match: match[1] + base, page.read_text()))
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    main()
