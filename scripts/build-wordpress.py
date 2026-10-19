"""Package the existing site as an installable WordPress theme."""

import json
import shutil
import zipfile
from pathlib import Path
import sys

sys.dont_write_bytecode = True
from build import compact, read_page

ROOT = Path(__file__).resolve().parent.parent


def main():
    output = ROOT / "dist/wordpress"
    theme = output / "alfred-kour"
    theme.mkdir(parents=True, exist_ok=True)
    shutil.copytree(ROOT / "wordpress/theme", theme, dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/public", theme / "assets", dirs_exist_ok=True)
    shutil.copytree(ROOT / "src/partials", theme / "partials", dirs_exist_ok=True)
    pages = []
    routes = set()
    for path in sorted((ROOT / "src/pages").rglob("*.html")):
        meta, content = read_page(path)
        route = meta["permalink"]
        if route in routes:
            raise ValueError(f"Duplicate route: {route}")
        routes.add(route)
        pages.append(dict(meta, content=compact(content)))
    (theme / "pages.json").write_text(json.dumps(pages, ensure_ascii=False, indent=2))
    archive = output / "alfred-kour.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(theme.rglob("*")):
            if path.is_file():
                bundle.write(path, path.relative_to(output))
    print(f"Packaged {len(pages)} pages: {archive}")


if __name__ == "__main__":
    main()
