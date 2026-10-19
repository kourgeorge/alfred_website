"""Check all migrated routes against the source content (read-only)."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path
import sys
from urllib.request import urlopen

sys.dont_write_bytecode = True
from build import read_page


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.lang = self.direction = ''
        self.iframes = []
        self.images = []
        self.headings = []
        self.in_h1 = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'html':
            self.lang, self.direction = attrs.get('lang'), attrs.get('dir')
        if tag == 'iframe':
            self.iframes.append(attrs.get('src'))
        if tag == 'img':
            self.images.append(attrs.get('src'))
        if tag == 'h1':
            self.in_h1 = True

    def handle_endtag(self, tag):
        if tag == 'h1':
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_h1 and data.strip():
            self.headings.append(data.strip())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    args = parser.parse_args()
    base = args.url.rstrip('/')
    root = Path(__file__).resolve().parent.parent

    def check(path):
        meta, content = read_page(path)
        expected = Document(content)
        url = base + meta['permalink']
        try:
            with urlopen(url, timeout=30) as response:
                actual = Document(response.read().decode())
            assert actual.lang == meta['lang'], 'language differs'
            assert actual.direction == ('rtl' if meta['lang'] in ('he', 'ar') else 'ltr'), 'direction differs'
            assert actual.headings == expected.headings, 'headings differ'
            assert actual.iframes == expected.iframes, 'video/form embeds differ'
            for image in expected.images:
                suffix = '/assets' + image if image.startswith('/') else image
                assert any(src.endswith(suffix) for src in actual.images), f'missing image: {image}'
            return None
        except Exception as error:
            return f'{url}: {error}'

    paths = sorted((root / 'src/pages').rglob('*.html'))
    with ThreadPoolExecutor(max_workers=5) as pool:
        failures = list(filter(None, pool.map(check, paths)))
    for failure in failures:
        print(failure)
    print(f'{len(paths) - len(failures)}/{len(paths)} pages passed')
    return bool(failures)


if __name__ == '__main__':
    sys.exit(main())
