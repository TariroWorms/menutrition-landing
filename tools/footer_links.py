#!/usr/bin/env python3
"""Add the «For dietitians» link to the footer of every built page (run after the builders; idempotent).
    python3 tools/footer_links.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T = json.loads((ROOT / 'tools' / 'pages' / 'dietitians.json').read_text(encoding='utf-8'))
LANG = re.compile(r'<html lang="([a-zA-Z-]+)"')
TERMS = re.compile(r'(<footer>.*?<a href="/terms[^"]*">[^<]*</a>)', re.S)
n = 0
for p in ROOT.rglob('*.html'):
    if any(x in p.parts for x in ('tools', 'node_modules', '.git', 'photo-review')):
        continue
    s = p.read_text(encoding='utf-8')
    if 'class="fdt"' in s or '<footer>' not in s:
        continue
    m = LANG.search(s)
    lang = (m.group(1) if m else 'en').split('-')[0]
    if lang not in T:
        lang = 'en'
    href = '/for-dietitians/' if lang == 'en' else f'/{lang}/for-dietitians/'
    link = f'<a class="fdt" href="{href}">{T[lang]["h1"]}</a>'
    s2, k = TERMS.subn(lambda m: m.group(1) + link, s, count=1)
    if k:
        p.write_text(s2, encoding='utf-8')
        n += 1
print(n, 'pages')
