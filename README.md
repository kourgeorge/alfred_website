# Alfred Kour website

Complete published static website recovered from https://alfred.kour.me/ on 2026-10-18.

Edit the files in `src/`, then build the site into `dist/` (`dist/` is not stored in Git):

```sh
python3 scripts/build.py
python3 -m http.server 8000 --directory dist
```

```
src/
  pages/        one file per page, grouped by language
    he/           Hebrew (main site): home.html, about.html, theory-course.html, blog/...
    en/ ar/ ru/   translated sections, using the same file names as each other
    fr/           French page
    */legacy/     older pages still online at their old addresses
  partials/     shared headers and footers per language (he/header.html, ...)
  layouts/      the page shell: <head> and <body> wrapper
  public/       stylesheet and photos, copied into dist/ as they are
scripts/
  build.py      builds src/ into dist/
```

Each page file starts with a short settings block, then its main content:

```
---
title: אודות אלפרד קור | אלפרד קור
description: ...
lang: he
permalink: /about_us/
---
<main>...</main>
```

`permalink` is the page's web address. File names describe the page; web
addresses stay as they were on the published site, so existing links keep working.
Pages use their language's `header.html` and `footer.html` unless the settings name
another one (for example `header: he/home-header`).

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

## WordPress migration

The site was imported into WordPress at `http://192.168.1.77/` using the custom
Alfred Kour theme. All 74 source pages, including the blog and legacy addresses,
are WordPress Pages. Find them under **Pages → All Pages**. Their HTML is available
in the classic editor's **Text** tab; use this tab to preserve the existing layout
when editing. Page edits in WordPress do not sync back into this repository.

Theme source is in `wordpress/theme/`. Build an uploadable theme from the current
source with:

```sh
python3 scripts/build-wordpress.py
python3 scripts/check-wordpress.py http://192.168.1.77
```

The ZIP is `dist/wordpress/alfred-kour.zip`. Install it under **Appearance → Themes
→ Add Theme → Upload Theme**, activate it, then run **Tools → Alfred migration**.
The importer creates missing pages and sets the Hebrew homepage. Re-running it
preserves existing imported page content. Updating the theme updates shared
headers, footers, stylesheet and bundled photographs, but does not overwrite page
edits in WordPress. Original addresses are provided by the active theme's rewrite
rules; the server must route missing files to WordPress as usual.

The original WordPress homepage settings are saved in the
`alfred_kour_previous_home` option. To roll back, reactivate the previous theme and
restore **Settings → Reading** (previously the latest posts). Existing WordPress
posts and pages are retained. No public DNS or original hosting changes are made
by the migration. External course purchases, forms and videos continue to use
their existing services.
