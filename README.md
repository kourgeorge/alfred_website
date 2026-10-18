# Alfred Kour website

Complete published static website recovered from https://alfred.kour.me/ on 2026-10-18.

The `dist/` directory contains 69 HTML pages, the stylesheet, photographs, and a script referenced by the published pages. Serve this directory as the web root. No build step is required:

```sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000. Internal links use absolute paths from the web root.

`recovery-manifest.json` lists downloaded URLs, file paths, and SHA-256 checksums. `.openai/hosting.json` preserves the original Sites project identity and static directory.

This is a recovery of the deployed files, not an export of the original source repository or Git history. Unpublished files, build scripts, and the original `course-lectures.json` were not accessible. Google Forms, Teachable courses, YouTube videos, and other external services remain linked and are not copied into this repository. Pages may contain hosting-injected Cloudflare code.
