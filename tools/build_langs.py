#!/usr/bin/env python3
"""Build the 20 language pages (/de/, /ru/, /ar/ …) from index.html.

index.html (English) stays the single source: markup, styles, scripts and the I18N
dictionary. For every language this script writes <lang>/index.html with the text
already translated in the HTML (search engines see it without running JS), its own
<title>, description, canonical and Open Graph tags, and the same hreflang block.
The hreflang block in index.html itself is refreshed too.

Run from the repo root after any change to index.html:
    python3 tools/build_langs.py
"""
import datetime
import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://menutrition.app/'
RTL = {'ar', 'he'}
HREFLANG = {'zh': 'zh-Hans'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta',
        'source', 'track', 'wbr'}

# "AI calorie counter" for the <title> and description of each language page.
AI_COUNTER = {
    'en': 'AI calorie counter',
    'de': 'KI-Kalorienzähler',
    'es': 'Contador de calorías con IA',
    'fr': 'Compteur de calories IA',
    'id': 'Penghitung kalori AI',
    'it': 'Contacalorie con IA',
    'nl': 'AI-calorieënteller',
    'pl': 'Licznik kalorii AI',
    'pt': 'Contador de calorias com IA',
    'sv': 'AI-kaloriräknare',
    'vi': 'Ứng dụng đếm calo AI',
    'tr': 'Yapay zekâ kalori sayacı',
    'uk': 'ШІ-лічильник калорій',
    'ru': 'ИИ-счётчик калорий',
    'ar': 'عداد السعرات الحرارية بالذكاء الاصطناعي',
    'he': 'מונה קלוריות מבוסס AI',
    'hi': 'AI कैलोरी काउंटर',
    'th': 'แอปนับแคลอรี่ด้วย AI',
    'zh': 'AI 卡路里计算器',
    'ja': 'AIカロリー計算アプリ',
    'ko': 'AI 칼로리 계산기',
}


class I18nSpans(HTMLParser):
    """Finds the content span (start, end offsets) of every data-i18n / data-i18n-html element."""

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self.src = src
        self.line_starts = [0] + [m.end() for m in re.finditer('\n', src)]
        self.stack = []   # [tag, key, kind, content_start]
        self.spans = []   # (start, end, key, kind)

    def abs_pos(self):
        line, col = self.getpos()
        return self.line_starts[line - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag in VOID:
            return
        a = dict(attrs)
        key, kind = (a['data-i18n'], 'text') if 'data-i18n' in a else \
                    (a['data-i18n-html'], 'html') if 'data-i18n-html' in a else (None, None)
        self.stack.append([tag, key, kind, self.abs_pos() + len(self.get_starttag_text())])

    def handle_endtag(self, tag):
        while self.stack:
            t, key, kind, start = self.stack.pop()
            if key:
                self.spans.append((start, self.abs_pos(), key, kind))
            if t == tag:
                break


def strip_tags(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()


def page_url(lang):
    return SITE if lang == 'en' else f'{SITE}{lang}/'


def set_meta(src, attr, name, value):
    pat = re.compile(r'(<meta %s="%s" content=")[^"]*(")' % (attr, re.escape(name)))
    assert pat.search(src), name
    return pat.sub(lambda m: m.group(1) + html.escape(value) + m.group(2), src, count=1)


# Popular dishes shown on the home page (section #dishes); links lead to the dish pages.
POPULAR = ['kabsa', 'shawarma', 'pizza_margherita', 'chicken_biryani', 'pad_thai', 'hummus', 'tonkotsu_ramen', 'borscht']
DISH_INDEX_MIN = 100   # a language gets its own /<lang>/dishes/ link once it has this many dish pages


def dish_links(lang):
    """(href of the dish list, cards HTML) for the home page in this language."""
    data = {x['w'].replace(' ', '_'): x for x in json.loads((ROOT / 'dishes' / 'search.json').read_text(encoding='utf-8'))}
    own = lang != 'en' and sum(1 for x in data.values() if lang in x.get('l', [])) >= DISH_INDEX_MIN
    index = f'/{lang}/dishes/' if own else '/dishes/'
    ui = json.loads((ROOT / 'tools' / 'dishes' / 'ui.json').read_text(encoding='utf-8'))
    U = ui.get(lang, ui['en'])
    cards = []
    for k in POPULAR:
        x = data.get(k)
        if not x or 'u' not in x:
            continue
        local = lang in x.get('l', [])
        href = (f'/{lang}' if local and lang != 'en' else '') + f'/dishes/{x["u"]}/'
        name = x['n'][lang] if local else x['n']['en']
        cards.append(f'<a class="dg-card" href="{href}"><span class="em">{x["e"]}</span><span>{html.escape(name)}'
                     f'<small>{x["k"]} {html.escape(U["kcal"])} / 100 {html.escape(U["g"])}</small></span></a>')
    return index, '\n'.join(cards)


def put_dishes(doc, lang):
    index, cards = dish_links(lang)
    doc = re.sub(r'<!-- dishes:start -->.*?<!-- dishes:end -->',
                 lambda m: f'<!-- dishes:start -->\n{cards}\n<!-- dishes:end -->', doc, flags=re.S)
    return re.sub(r'href="[^"]*"( class="[^"]*")? data-dishes-link', lambda m: f'href="{index}"{m.group(1) or ""} data-dishes-link', doc)


def main():
    path = ROOT / 'index.html'
    src = path.read_text(encoding='utf-8')
    i18n = json.loads(re.search(r'const I18N = (\{.*?\});\n', src, re.S).group(1))
    langs = ['en'] + list(i18n)

    # hreflang block, shared by every page
    links = [f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{page_url(l)}" />' for l in langs]
    links.append(f'<link rel="alternate" hreflang="x-default" href="{SITE}" />')
    block = '<!-- hreflang:start (tools/build_langs.py) -->\n' + '\n'.join(links) + '\n<!-- hreflang:end -->'
    if '<!-- hreflang:start' in src:
        src = re.sub(r'<!-- hreflang:start.*?<!-- hreflang:end -->', lambda m: block, src, flags=re.S)
    else:
        src = src.replace('<link rel="canonical"', block + '\n<link rel="canonical"', 1)
    src = put_dishes(src, 'en')
    path.write_text(src, encoding='utf-8')

    p = I18nSpans(src)
    p.feed(src)
    p.close()
    spans = sorted(p.spans)
    base_text = {k: html.unescape(src[s:e]).strip() for s, e, k, kind in spans if kind == 'text'}

    for lang, t in i18n.items():
        out, pos = [], 0
        for s, e, key, kind in spans:
            if key not in t:
                continue
            out.append(src[pos:s])
            out.append(t[key] if kind == 'html' else html.escape(t[key], quote=False))
            pos = e
        out.append(src[pos:])
        doc = put_dishes(''.join(out), lang)

        # translated placeholders (data-i18n-ph)
        doc = re.sub(r'placeholder="[^"]*"( data-i18n-ph="(\w+)")',
                     lambda m: f'placeholder="{html.escape(t.get(m.group(2), ""), quote=True)}"{m.group(1)}' if m.group(2) in t else m.group(0), doc)
        dir_attr = ' dir="rtl"' if lang in RTL else ''
        doc = doc.replace('<html lang="en">', f'<html lang="{lang}"{dir_attr} data-page-lang="{lang}">', 1)

        slogan = t.get('slogan', base_text['slogan'])
        amp = strip_tags(t.get('hero_amp', 'Smartest AI.'))
        hero_p = t.get('hero_p', base_text['hero_p'])
        title = f'Me Nutrition — {slogan} {amp} {AI_COUNTER[lang]}'
        desc = f'Me Nutrition — {AI_COUNTER[lang]}. {hero_p}'
        og_title = f'Me Nutrition — {slogan} {amp}'
        doc = re.sub(r'<title>.*?</title>', lambda m: f'<title>{html.escape(title, quote=False)}</title>', doc, count=1)
        doc = set_meta(doc, 'name', 'description', desc)
        doc = set_meta(doc, 'property', 'og:title', og_title)
        doc = set_meta(doc, 'property', 'og:description', hero_p)
        doc = set_meta(doc, 'property', 'og:url', page_url(lang))
        doc = set_meta(doc, 'name', 'twitter:title', og_title)
        doc = set_meta(doc, 'name', 'twitter:description', hero_p)
        doc = doc.replace(f'<link rel="canonical" href="{SITE}" />',
                          f'<link rel="canonical" href="{page_url(lang)}" />', 1)
        # the page lives one folder down: shared images are one level up
        doc = re.sub(r'''(["'(])(shots|badges)/''', r'\1../\2/', doc)

        d = ROOT / lang
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(doc, encoding='utf-8')
        print(f'{lang}/index.html  {len(doc.encode()) // 1024} KB  {title}')

    write_sitemap(langs)


def write_sitemap(langs):
    """sitemap.xml: every language page with its hreflang alternates, plus /privacy and /terms."""
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{page_url(l)}"/>' for l in langs)
    alts += f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}"/>'
    urls = [f'  <url>\n    <loc>{page_url(l)}</loc>\n    <lastmod>{today}</lastmod>'
            f'\n    <priority>{"1.0" if l == "en" else "0.9"}</priority>{alts}\n  </url>' for l in langs]
    urls += [f'  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.3</priority>\n  </url>'
             for p in ('privacy', 'terms')]
    (ROOT / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + '\n'.join(urls) + '\n</urlset>\n', encoding='utf-8')


if __name__ == '__main__':
    main()
