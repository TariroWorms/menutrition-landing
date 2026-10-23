#!/usr/bin/env python3
"""Build the food pages: /foods/<slug>/, category pages /foods/<category>/ (paged) and the /foods/ index, in 5 languages.

Data: foods_data.json (nutrition per 100 g from USDA FoodData Central and ANSES CIQUAL, names in 5 languages),
texts: foods_ui.json. Shares header/footer/language switcher helpers and the stylesheet with the dishes pages.
Writes <out>/[<lang>/]foods/..., <out>/foods/food.css and <out>/sitemap-foods-<lang>.xml.
"""
import argparse
import bisect
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'dishes'))
import build_dishes as bd   # noqa: E402  (helpers only; its main() is not run)

esc, fill, SITE, RTL, LANG_NAMES = bd.esc, bd.fill, bd.SITE, bd.RTL, bd.LANG_NAMES
LANGS = ['en', 'ru', 'ar', 'it', 'el', 'es', 'de']
DISH_LANGS = {'en', 'ru', 'ar', 'it', 'el'}   # languages the dishes catalogue exists in
PAGE = 300                 # foods per category page
COMMA = {'ru', 'it', 'el', 'es', 'de'}  # decimal comma
SRC_KEY = {'sr': 'src_sr', 'fd': 'src_fd', 'ciqual': 'src_ciqual'}
SRC_URL = {'sr': 'https://fdc.nal.usda.gov/', 'fd': 'https://fdc.nal.usda.gov/', 'ciqual': 'https://ciqual.anses.fr/'}


def fpath(lang, *parts):
    base = '/' if lang == 'en' else f'/{lang}/'
    return base + 'foods/' + ''.join(f'{p}/' for p in parts)


def nf(lang, x, d=1):
    s = f'{round(x, d):.{d}f}'.rstrip('0').rstrip('.') if d else str(int(x + 0.5))
    return s.replace('.', ',') if lang in COMMA else s


def slugify(s):
    s = re.sub(r'[^a-z0-9]+', '-', s.lower().replace("'", '')).strip('-')
    return s[:70].strip('-') or 'food'


def related(f, by_cat_token, by_cat, kcals):
    """Up to 6 foods of the same category: first the ones starting with the same word, then the closest by calories."""
    out, seen = [], {f['key']}
    for g in sorted(by_cat_token[(f['category'], f['token'])], key=lambda g: abs(g['kcal'] - f['kcal'])):
        if g['key'] not in seen and len(out) < 6:
            out.append(g); seen.add(g['key'])
    if len(out) < 6:
        arr = by_cat[f['category']]
        i = bisect.bisect_left(kcals[f['category']], f['kcal'])
        for d in range(1, len(arr)):
            for j in (i - d, i + d - 1):
                if 0 <= j < len(arr) and arr[j]['key'] not in seen and len(out) < 6:
                    out.append(arr[j]); seen.add(arr[j]['key'])
            if len(out) >= 6:
                break
    return out


class Builder:
    def __init__(self, out, data, S, ui, template, cssv):
        self.out, self.F, self.S, self.ui, self.tpl, self.cssv = Path(out), data, S, ui, template, cssv
        self.langs = [l for l in LANGS if l in S and l in ui]
        self.sitemap = {l: [] for l in self.langs}

    def write(self, lang, url_path, html, sitemap=True):
        p = self.out / url_path.strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(html, encoding='utf-8')
        if sitemap:
            self.sitemap[lang].append(SITE + url_path)

    def shell(self, lang, title, desc, url_path, alt, main, jsonld, script=''):
        s, u = self.S[lang], self.ui[lang]
        values = {
            'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(title), 'description': esc(desc),
            'url': SITE + url_path, 'robots': '',
            'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + alt(l)}" />' for l in self.langs)
                        + f'\n<link rel="alternate" hreflang="x-default" href="{SITE + alt("en")}" />',
            'cssv': self.cssv, 'jsonld': jsonld, 'home': bd.home(lang), 'foods_href': fpath(lang),
            'dishes_href': bd.path(lang if lang in DISH_LANGS else 'en'), 'langmenu': bd.lang_menu(lang, self.langs, alt), 'main': main,
            'langs': ''.join(f'<a href="{alt(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in self.langs), 'script': script,
        }
        values.update({f'ui.{k}': bd.brand(esc(v)) for k, v in u.items() if isinstance(v, str)})
        values.update({f's.{k}': esc(v) for k, v in s.items() if isinstance(v, str)})
        return fill(self.tpl, values)

    def crumbs(self, lang, tail, cat=None):
        s = self.S[lang]
        parts = [f'<a href="{bd.home(lang)}">{esc(s["home_crumb"])}</a>', f'<a href="{fpath(lang)}">{esc(s["foods"])}</a>']
        if cat:
            parts.append(f'<a href="{fpath(lang, cat)}">{esc(s["cats"][cat])}</a>')
        return '<nav class="crumbs">' + ' › '.join(parts + [esc(tail)]) + '</nav>'

    def ld(self, lang, trail):
        items = [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + u} for i, (n, u) in enumerate(trail)]
        return ('<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                                                                  'itemListElement': items}, ensure_ascii=False) + '</script>')

    # ---- a food page ----
    def food_page(self, lang, f, rel):
        s, u = self.S[lang], self.ui[lang]
        name, k = f['names'][lang], f['kcal']
        n1 = lambda x: nf(lang, x, 1)
        kcal_from = {'protein': f['protein'] * 4, 'fat': f['fat'] * 9, 'carbs': f['carbs'] * 4}
        total = sum(kcal_from.values()) or 1
        pct = {m: round(100 * v / total) for m, v in kcal_from.items()}
        colors = {'protein': '#2E7A6F', 'fat': '#C9A35B', 'carbs': '#8DA7C9'}
        macros = ''.join(
            f'<div class="macro"><b>{n1(f[m])} {esc(u["g"])}</b><span>{esc(u[m])}</span><em>{esc(s["per100"])}</em>'
            f'<i style="--w:{pct[m]}%;--c:{colors[m]}"></i></div>' for m in ('protein', 'fat', 'carbs'))
        lead = s['lead'].format(name=name, kcal=nf(lang, k, 0), p=n1(f['protein']), f=n1(f['fat']), c=n1(f['carbs']))
        weights = (50, 100, 150, 200, 250)
        rows = ''.join(f'<tr><td>{w} {esc(u["g"])}</td><td>{nf(lang, k * w / 100, 0)} {esc(u["kcal"])}</td></tr>' for w in weights)
        more = ''
        for key, unit in (('fiber', u['g']), ('sugar', u['g']), ('sat_fat', u['g']), ('sodium_mg', s['mg'])):
            if key in f:
                label = s['sodium'] if key == 'sodium_mg' else s[key]
                more += f'<div><b>{n1(f[key]) if key != "sodium_mg" else nf(lang, f[key], 0)} {esc(unit)}</b><span>{esc(label)}</span></div>'
        more_html = f'<section><h2>{esc(s["more_h"])}</h2><div class="more">{more}</div></section>' if more else ''
        rel_html = ''.join(
            f'<a href="{fpath(lang, g["slug"])}"><div>{esc(g["names"][lang])}'
            f'<span>{nf(lang, g["kcal"], 0)} {esc(u["kcal"])} / 100 {esc(u["g"])}</span></div></a>' for g in rel)
        cat = f['category']
        main = f'''{self.crumbs(lang, name, cat)}
  <h1>{esc(name)}</h1>
  <a class="fcat" href="{fpath(lang, cat)}">{esc(s["cats"][cat])}</a>
  <section class="card nut first" style="margin-top:20px">
    <div><div class="fkcal"><span class="big">{nf(lang, k, 0)}</span><small>{esc(u["kcal"])}</small></div><div class="lbl">{esc(s["per100"])}</div></div>
    <div class="macros" style="grid-column:1/-1">{macros}</div>
  </section>
  <p class="intro">{esc(lead)}</p>
  <p class="fsrc" style="margin-top:8px">{esc(s["split_h"])}: {esc(s["split_p"].format(p=pct["protein"], f=pct["fat"], c=pct["carbs"]))}</p>
  <section>
    <h2>{esc(s["weight_h"])}</h2>
    <div class="wcalc"><label for="w">{esc(s["weight_lbl"])}</label><input id="w" type="number" inputmode="decimal" min="0" max="5000" value="100" data-k="{k}" data-t="{esc(s["weight_res"])}"><b id="wr">{esc(s["weight_res"].format(n=nf(lang, k, 0)))}</b></div>
    <table class="wtab"><thead><tr><th>{esc(s["weight_col"])}</th><th>{esc(s["kcal_col"])}</th></tr></thead><tbody>{rows}</tbody></table>
  </section>
  {more_html}
  <section><h2>{esc(s["related_h"])}</h2><div class="related">{rel_html}</div>
  <p class="note" style="margin-top:12px"><a href="{fpath(lang, cat)}">{esc(s["cat_all"].format(cat=s["cats"][cat]))} →</a></p></section>
  <section class="card cta"><h2>{esc(s["snap_h"])}</h2><p>{esc(s["snap_p"])}</p><a class="btn" href="https://apps.apple.com/app/id6767123368?pt=128869855&amp;ct=food-cta-{lang}&amp;mt=8" target="_blank" rel="noopener">{esc(u["cta_btn"])}</a></section>
  <p class="fsrc">{esc(s["source"])}: <a href="{SRC_URL[f["src"]]}" rel="noopener" target="_blank">{esc(s[SRC_KEY[f["src"]]])}</a>. {esc(s["note"])}</p>'''
        script = f'<script src="/foods/food.js?v={self.cssv}" defer></script>'
        desc = s['meta'].format(name=name, kcal=nf(lang, k, 0), p=n1(f['protein']), f=n1(f['fat']), c=n1(f['carbs']))
        title = s['title'].format(name=name)
        url = fpath(lang, f['slug'])
        html = self.shell(lang, title, desc, url, lambda l: fpath(l, f['slug']), main,
                          self.ld(lang, [(s['foods'], fpath(lang)), (s['cats'][cat], fpath(lang, cat)), (name, url)]), script)
        self.write(lang, url, html)

    # ---- category pages (paged) ----
    def category_pages(self, lang, cat, items):
        s, u = self.S[lang], self.ui[lang]
        cname = s['cats'][cat]
        items = sorted(items, key=lambda f: f['names'][lang].lower())
        pages = max(1, -(-len(items) // PAGE))
        for p in range(1, pages + 1):
            chunk = items[(p - 1) * PAGE:p * PAGE]
            alt = (lambda l, p=p: fpath(l, cat) if p == 1 else fpath(l, cat, 'page', p))
            cards = ''.join(
                f'<a href="{fpath(lang, f["slug"])}"><span class="em">🍽️</span><div>{esc(f["names"][lang])}'
                f'<span>{nf(lang, f["kcal"], 0)} {esc(u["kcal"])} / 100 {esc(u["g"])}</span></div></a>' for f in chunk)
            nav = ''
            if pages > 1:
                back = fpath(lang, cat) if p == 2 else fpath(lang, cat, 'page', p - 1)
                prev = f'<a href="{back}">{esc(s["prev"])}</a>' if p > 1 else '<span></span>'
                nxt = f'<a href="{fpath(lang, cat, "page", p + 1)}">{esc(s["next"])}</a>' if p < pages else '<span></span>'
                nav = f'<div class="pager">{prev}<span>{esc(s["page_of"].format(p=p, n=pages))}</span>{nxt}</div>'
            h1 = cname if p == 1 else f'{cname} — {s["page_of"].format(p=p, n=pages)}'
            main = (f'{self.crumbs(lang, cname)}<h1>{esc(h1)}</h1><p class="intro">{esc(s["cat_p"].format(n=len(items)))}</p>'
                    f'<div class="related" style="margin-top:22px">{cards}</div>{nav}<p class="fsrc">{esc(s["note"])}</p>')
            url = alt(lang)
            title = s['cat_title'].format(cat=cname) + ('' if p == 1 else f' — {s["page_of"].format(p=p, n=pages)}')
            desc = s['cat_meta'].format(n=len(items), cat=cname)
            self.write(lang, url, self.shell(lang, title, desc, url, alt, main,
                                             self.ld(lang, [(s['foods'], fpath(lang)), (cname, fpath(lang, cat))])))

    # ---- index with search ----
    def index_page(self, lang, counts):
        s, u = self.S[lang], self.ui[lang]
        total = sum(counts.values())
        dl = lang if lang in DISH_LANGS else 'en'
        cards = ''.join(f'<a href="{fpath(lang, c)}">{esc(s["cats"][c])}<small>{esc(s["foods_n"].format(n=counts[c]))}</small></a>'
                        for c in self.S['_cats'] if counts.get(c))
        main = (
                f'<nav class="crumbs"><a href="{bd.home(lang)}">{esc(s["home_crumb"])}</a> › {esc(s["foods"])}</nav>'
                f'<h1>{esc(s["index_h"])}</h1><p class="intro">{esc(s["index_p"].format(n=f"{total:,}".replace(",", " ")))}</p>'
                f'<input class="search" id="q" type="search" placeholder="{esc(s["search_ph"])}" aria-label="{esc(s["search_ph"])}" autocomplete="off">'
                f'<div class="sres" id="res"></div><p class="empty" id="none" hidden>{esc(s["search_none"])}</p>'
                f'<h2 style="margin-top:28px">{esc(s["cats_h"])}</h2><div class="catgrid">{cards}</div>'
                f'<p class="note" style="margin-top:22px"><a href="{bd.path(dl)}">{esc(s["dishes_link"])}</a></p><p class="fsrc">{esc(s["note"])}</p>')
        script = '''<script>(function(){var q=document.getElementById('q'),res=document.getElementById('res'),none=document.getElementById('none'),D=null,L=%s;
function load(cb){if(D)return cb();fetch(L).then(function(r){return r.json()}).then(function(j){D=j;cb()})}
function run(){var t=q.value.trim().toLowerCase();res.innerHTML='';none.hidden=true;if(t.length<2)return;var w=t.split(/\\s+/),out=[];
for(var i=0;i<D.length&&out.length<30;i++){var n=D[i][0].toLowerCase(),ok=true;for(var j=0;j<w.length;j++){if(n.indexOf(w[j])<0){ok=false;break}}if(ok)out.push(D[i])}
if(!out.length){none.hidden=false;return}
out.forEach(function(d){var a=document.createElement('a');a.href=%s+d[1]+'/';var n=document.createElement('div');n.textContent=d[0];var k=document.createElement('span');k.textContent=d[2]+' %s';a.appendChild(n);a.appendChild(k);res.appendChild(a)})}
q.addEventListener('focus',function(){load(function(){})});q.addEventListener('input',function(){load(run)});})();</script>''' % (
            json.dumps(fpath(lang) + 'search.json'), json.dumps(fpath(lang)), esc(u['kcal']))
        url = fpath(lang)
        self.write(lang, url, self.shell(lang, s['index_title'], s['index_meta'].format(n=f'{total:,}'.replace(',', ' ')), url,
                                         lambda l: fpath(l), main, self.ld(lang, [(s['foods'], url)]), script))

    def search_json(self, lang):
        rows = sorted(([f['names'][lang], f['slug'], round(f['kcal'])] for f in self.F), key=lambda r: r[0].lower())
        p = self.out / fpath(lang).strip('/') / 'search.json'
        p.write_text(json.dumps(rows, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(HERE.parent.parent))
    ap.add_argument('--limit', type=int, help='build only the first N foods (testing)')
    a = ap.parse_args()
    out = Path(a.out)
    data = json.load(open(HERE / 'foods_data.json', encoding='utf-8'))
    if a.limit:
        data = data[:a.limit]
    S = json.load(open(HERE / 'foods_ui.json', encoding='utf-8'))
    ui = json.load(open(HERE.parent / 'dishes' / 'ui.json', encoding='utf-8'))
    ui.update(S.get('_common', {}))
    # stylesheet: dishes CSS + foods CSS, one file for all pages
    dishes_tpl = (HERE.parent / 'dishes' / 'template.html').read_text(encoding='utf-8')
    css = re.search(r'<style>(.*?)</style>', dishes_tpl, re.S).group(1) + '\n' + (HERE / 'food.css').read_text(encoding='utf-8')
    cssv = hashlib.md5((css + (HERE / 'food.js').read_text(encoding='utf-8')).encode()).hexdigest()[:8]
    tpl = (HERE / 'template.html').read_text(encoding='utf-8')

    # unique slugs from the English name; a category name is reserved
    used, reserved = set(), set(S['_cats']) | {'search', 'page'}
    for f in data:
        base = slugify(f['names']['en'])
        if base in reserved:
            base += '-food'
        slug, i = base, 2
        while slug in used:
            slug, i = f'{base}-{i}', i + 1
        used.add(slug); f['slug'] = slug
        f['token'] = re.split(r'[\s,]+', f['names']['en'].lower())[0]
    by_cat, by_cat_token = {}, {}
    for f in sorted(data, key=lambda f: f['kcal']):
        by_cat.setdefault(f['category'], []).append(f)
        by_cat_token.setdefault((f['category'], f['token']), []).append(f)
    kcals = {c: [g['kcal'] for g in v] for c, v in by_cat.items()}
    B = Builder(out, data, S, ui, tpl, cssv)
    for lang in B.langs:
        d = out / fpath(lang).strip('/')
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
        for f in data:
            B.food_page(lang, f, related(f, by_cat_token, by_cat, kcals))
        for c, items in by_cat.items():
            B.category_pages(lang, c, items)
        B.index_page(lang, {c: len(v) for c, v in by_cat.items()})
        B.search_json(lang)
        urls = ''.join(f'<url><loc>{u}</loc></url>\n' for u in B.sitemap[lang])
        (out / f'sitemap-foods-{lang}.xml').write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '</urlset>\n',
            encoding='utf-8')
        print(lang, len(B.sitemap[lang]), 'urls')
    (out / 'foods' / 'food.css').write_text(css, encoding='utf-8')
    (out / 'foods' / 'food.js').write_text((HERE / 'food.js').read_text(encoding='utf-8'), encoding='utf-8')


if __name__ == '__main__':
    main()
