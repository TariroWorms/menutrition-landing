#!/usr/bin/env python3
"""Feature pages: /features/<slug>/ (English) and /<lang>/features/<slug>/ for every site language.

Texts: tools/features/features.json ({slug: {lang: {...}}}, interface words in "_ui").
Layout and styles are shared with the dish pages (tools/dishes/template.html).
    python3 tools/features/build_features.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / 'dishes'))
from build_dishes import LANG_NAMES, RTL, SITE, brand, esc, fill, lang_menu, md  # noqa: E402

STORE = 'https://apps.apple.com/app/id6767123368'


def fpath(lang, slug=None):
    return ('/' if lang == 'en' else f'/{lang}/') + 'features/' + (f'{slug}/' if slug else '')


def home(lang):
    return '/' if lang == 'en' else f'/{lang}/'


def local(lang, section):
    """/<lang>/<section>/ when that section exists in the language, else the English one."""
    return f'/{lang}/{section}/' if lang != 'en' and (ROOT / lang / section / 'index.html').exists() else f'/{section}/'


def glist(items, kind=''):
    out = ''
    for x in items:
        em, _, rest = x.partition(' ')
        out += f'<li><span class="ie">{em}</span><span>{md(rest)}</span></li>'
    return f'<section class="gs {kind}"><ul class="glist">{out}</ul></section>'


def page(lang, slug, F, langs, template):
    U, T, meta = F['_ui'][lang], F[slug][lang], F['_meta'][slug]
    steps = ''.join(f'<li><span class="sn">{i}</span><span>{md(s.partition(" ")[2])}</span><span class="ie">{s.partition(" ")[0]}</span></li>'
                    for i, s in enumerate(T['steps'], 1))
    faq = ''.join(f'<details class="faq"><summary>{esc(q)}</summary><p>{brand(esc(a))}</p></details>' for q, a in T['faq'])
    more = ''.join(f'<a href="{fpath(lang, s)}"><span class="em">{F["_meta"][s]["emoji"]}</span><div>{esc(F[s][lang]["name"])}</div></a>'
                   for s in F['_order'] if s != slug and lang in F[s])
    ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang,
           'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in T['faq']]},
          {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': 'Me Nutrition',
           'operatingSystem': 'iOS', 'applicationCategory': 'HealthApplication', 'url': SITE + '/', 'downloadUrl': STORE,
           'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}}]
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(T['title']), 'description': esc(T['meta']),
        'url': SITE + fpath(lang, slug), 'home': home(lang), 'index': fpath(lang),
        'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + fpath(l, slug)}" />' for l in langs),
        'jsonld': '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld),
        'hero_cls': ' has-shot', 'emoji': meta['emoji'], 'name': brand(esc(T['name'])), 'lead': brand(md(T['lead'])),
        'shot': f'<img class="fshot" src="{meta["shot"]}" width="{meta["shot_w"]}" height="{meta["shot_h"]}" alt="{esc(T["name"])}" loading="lazy">',
        'steps': f'<ol class="steps">{steps}</ol>', 'benefits': glist(T['benefits'], 'can'), 'faq': faq,
        'more': f'<div class="related">{more}</div>', 'store': f'{STORE}?ct=feat-cta-{lang}&amp;mt=8',
        'dishes': local(lang, 'dishes'), 'guides': local(lang, 'guides'),
        'langs': ''.join(f'<a href="{fpath(l, slug)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: fpath(l, slug)),
    }
    values.update({f'u.{k}': brand(esc(v)) for k, v in U.items()})
    return fill(template, values)


def index(lang, F, langs, template):
    U = F['_ui'][lang]
    cards = ''.join(f'<a href="{fpath(lang, s)}"><span class="em">{F["_meta"][s]["emoji"]}</span><div>{esc(F[s][lang]["name"])}'
                    f'<span>{brand(esc(F[s][lang]["lead"]))}</span></div></a>' for s in F['_order'] if lang in F[s])
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(U['index_title']), 'description': esc(U['index_meta']),
        'url': SITE + fpath(lang), 'home': home(lang), 'index': fpath(lang),
        'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + fpath(l)}" />' for l in langs),
        'jsonld': '', 'hero_cls': '', 'emoji': '✨', 'name': brand(esc(U['index_h'])), 'lead': brand(esc(U['index_p'])), 'shot': '',
        'steps': '', 'benefits': '', 'faq': '', 'more': f'<div class="related fidx">{cards}</div>', 'store': f'{STORE}?ct=feat-cta-{lang}&amp;mt=8',
        'dishes': local(lang, 'dishes'), 'guides': local(lang, 'guides'),
        'langs': ''.join(f'<a href="{fpath(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, fpath),
    }
    values.update({f'u.{k}': brand(esc(v)) for k, v in U.items()})
    page_html = fill(template, values)
    # the index has no steps/FAQ: drop the empty sections
    return re.sub(r'<section class="fsec"[^>]*>\s*<h2>[^<]*</h2>\s*</section>', '', page_html)


def main():
    F = json.loads((HERE / 'features.json').read_text(encoding='utf-8'))
    style = re.search(r'<style>.*?</style>', (HERE.parent / 'dishes' / 'template.html').read_text(encoding='utf-8'), re.S).group(0)
    tpl = (HERE / 'template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    langs = [l for l in F['_ui'] if all(l in F[s] for s in F['_order'])]
    urls = []
    for lang in langs:
        for slug in F['_order']:
            p = ROOT / fpath(lang, slug).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(page(lang, slug, F, langs, tpl), encoding='utf-8')
            urls.append(SITE + fpath(lang, slug))
        p = ROOT / fpath(lang).strip('/') / 'index.html'
        p.write_text(index(lang, F, langs, tpl), encoding='utf-8')
        urls.append(SITE + fpath(lang))
    (ROOT / 'sitemap-features.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in sorted(urls)) + '</urlset>\n', encoding='utf-8')
    print(f'{len(langs)} languages ({", ".join(langs)}) → {len(urls)} pages')


if __name__ == '__main__':
    main()
