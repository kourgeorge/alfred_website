# Alfred Kour website

Complete published static website recovered from https://alfred.kour.me/ on 2026-10-18.

Edit the files in `src/`, then build the site into `dist/` (`dist/` is not stored in Git):

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

- `src/pages/` has one file per page. Each starts with a short block of settings
  (title, description, language, which header and footer to use), followed by the
  page's main content.
- `src/partials/` has the shared headers and footers, one per language.
- `src/layouts/` has the page shell (the `<head>` and `<body>` wrapper).
- `src/static/` holds the stylesheet and photos, copied into `dist/` as they are.

The build puts each page back on a single line, so line breaks and indentation in
`src/` are only there to make editing easier. The source in `src/` was rebuilt from
the published pages; building it gives the same pages, without the Cloudflare
script the host added.

Open http://localhost:8000. Internal links use absolute paths from the web root.

The GitHub Pages site is published at https://kourgeorge.github.io/alfred_website/.
Pushes to `main` deploy automatically through `.github/workflows/pages.yml`.
The workflow runs `scripts/build.py`, then `scripts/prepare-pages.py` to copy `dist/` into `_site/` and
prefix internal URLs with the Pages base path.

`recovery-manifest.json` lists the downloaded URLs, file paths, and SHA-256 checksums of the original recovered files. `.openai/hosting.json` preserves the original Sites project identity and static directory.

This is a recovery of the deployed files, not an export of the original source repository or Git history. Unpublished files, build scripts, and the original `course-lectures.json` were not accessible. Google Forms, Teachable courses, YouTube videos, and other external services remain linked and are not copied into this repository. The published pages contained Cloudflare code added by the host; the build leaves it out.
