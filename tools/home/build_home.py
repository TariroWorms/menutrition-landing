#!/usr/bin/env python3
"""Home page of menutrition.app — a nutrition portal (/, /ru/, /de/ …).

The app landing page lives at /app/ (tools/build_langs.py). Texts: tools/home/home_i18n.json.
Also writes sitemap-home.xml. Run after the dish/food builds (it reads dishes/cook.json and dish.css).
"""
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'dishes'))
from sitenav import sitenav, _pre, D5, FOODS, CALC  # noqa: E402
from build_dishes import LANG_NAMES, RTL, GLOBE  # noqa: E402

SITE = 'https://menutrition.app'
HREFLANG = {'zh': 'zh-Hans'}
CITE = json.load(open(ROOT / 'tools' / 'cite.json', encoding='utf-8'))
POPULAR = ['kabsa', 'chicken-tikka-masala', 'pad-thai', 'greek-salad', 'tacos-al-pastor', 'shakshuka', 'paella-valenciana', 'tonkotsu-ramen']
CUISINES = ['italian', 'japanese', 'mexican', 'indian', 'french', 'turkish', 'lebanese', 'thai', 'greek', 'chinese', 'spanish', 'korean']
CHIPS = ['chicken', 'rice', 'egg', 'potato', 'beef', 'tomato', 'cheese', 'eggplant', 'shrimp', 'lentils', 'salmon', 'pasta']
APP = 'https://apps.apple.com/app/id6767123368?pt=128869855&ct=home-{lang}&mt=8'
esc = html.escape


def home_url(lang):
    return '/' if lang == 'en' else f'/{lang}/'


CSS = '''<style>
.hero{padding:34px 0 10px}.hero h1{font-size:clamp(32px,6vw,58px);line-height:1.06;margin:0}.hero h1 em{font-style:normal;color:var(--teal)}
.hero p{font-size:18px;color:var(--muted);max-width:660px;margin:16px 0 0}
.thesis{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:26px 0}
.thesis div{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px}.thesis b{display:block;font-size:16px}.thesis span{color:var(--muted);font-size:14px}
.cookbox{background:linear-gradient(135deg,#e7f1ee,#f6efe2);border-radius:26px;padding:26px;margin:30px 0}
.cookbox h2{margin:0 0 6px}.cookbox p{margin:0 0 14px;color:var(--muted)}
.cookbox form{display:flex;gap:8px}.cookbox input{flex:1;min-width:0;padding:14px 18px;border-radius:999px;border:1px solid var(--line);font:inherit;background:#fff}
.cookbox button{padding:14px 20px;border-radius:999px;border:0;background:#1f1b17;color:#fff;font:inherit;font-weight:700;cursor:pointer}
.pcs{display:flex;flex-wrap:wrap;gap:8px;margin-top:12px}.pcs a{padding:7px 13px;border-radius:999px;background:#fff;border:1px solid var(--line);font-size:14px;font-weight:600;text-decoration:none}
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px;margin:14px 0 30px}
.tile{display:block;background:var(--card);border:1px solid var(--line);border-radius:20px;padding:18px;text-decoration:none}
.tile:hover{border-color:var(--teal)}.tile .ti{font-size:30px;display:block}.tile b{display:block;font-size:17px;margin-top:8px}.tile span:last-child{color:var(--muted);font-size:14px}
.pop{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px;margin:14px 0 30px}
.pcard{text-decoration:none;background:var(--card);border:1px solid var(--line);border-radius:18px;overflow:hidden}.pcard img{width:100%;height:auto;aspect-ratio:1;object-fit:cover;display:block}
.pcard b{display:block;padding:10px 12px 0;font-size:15px}.pcard span{display:block;padding:2px 12px 12px;color:var(--muted);font-size:13px}
.appb{display:grid;grid-template-columns:1fr auto;gap:20px;align-items:center;background:#1f1b17;color:#f8f6f1;border-radius:26px;padding:26px;margin:30px 0}
.appb h2{margin:0;color:#fff}.appb p{color:#d8d2c6}.appb a.btn{display:inline-block;margin-top:10px;padding:12px 18px;border-radius:999px;background:#fff;color:#1f1b17;font-weight:800;text-decoration:none}
.appb a.more{color:#9fd3c7;margin-inline-start:14px}.appb img{width:150px;height:auto;border-radius:22px}
@media(max-width:600px){.appb{grid-template-columns:1fr}.appb img{display:none}.cookbox form{flex-direction:column}}
.hero{padding:26px 0 6px}.hero h1{font-size:clamp(30px,5vw,48px)}.hero p{font-size:17px;margin-top:12px}
.bento{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;margin:22px 0 34px}
.bt{position:relative;display:flex;flex-direction:column;justify-content:flex-end;min-height:190px;border-radius:26px;padding:22px;text-decoration:none;color:var(--ink,#1f1b17);overflow:hidden;border:1px solid var(--line);transition:transform .18s,box-shadow .18s}
.bt:hover{transform:translateY(-3px);box-shadow:0 14px 34px rgba(31,27,23,.12)}
.bt .ic{font-size:34px;line-height:1;display:block;margin-bottom:auto}
.bt h3{font-family:Fraunces,serif;font-size:24px;line-height:1.1;margin:14px 0 6px}.bt p{margin:0;font-size:15px;opacity:.78;max-width:420px}
.bt .go{position:absolute;top:18px;inset-inline-end:20px;width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.7);display:grid;place-items:center;font-weight:800}
.b-app{grid-column:span 4;min-height:300px;background:#1f1b17;color:#f8f6f1;border-color:#1f1b17}.b-app p{color:#d8d2c6;opacity:1}.b-app .go{background:#fff;color:#1f1b17}
.b-app img.ph{position:absolute;inset-inline-end:26px;bottom:-30px;width:170px;height:auto;border-radius:24px 24px 0 0;box-shadow:0 10px 40px rgba(0,0,0,.4)}
.b-app .txt{max-width:55%}.b-app a{text-decoration:none}.b-app .more{color:#9fd3c7;margin-inline-start:14px;font-size:15px}.b-app .btn{display:inline-block;margin-top:14px;padding:11px 17px;border-radius:999px;background:#fff;color:#1f1b17;font-weight:800;font-size:15px}
.b-calc{grid-column:span 2;background:linear-gradient(160deg,#f6e7c9,#f1d7a8)}
.b-cook{grid-column:span 3;min-height:250px;background:linear-gradient(135deg,#dcebe6,#c9e1d9)}
.b-cook form{display:flex;gap:6px;margin-top:12px}.b-cook input{flex:1;min-width:0;padding:11px 15px;border-radius:999px;border:1px solid var(--line);font:inherit;background:#fff}
.b-cook button{padding:11px 16px;border-radius:999px;border:0;background:#1f1b17;color:#fff;font:inherit;font-weight:700;cursor:pointer}
.b-dish{grid-column:span 3;min-height:250px;background:#f3ece0}.b-dish .mos{position:absolute;inset-inline-end:16px;top:16px;display:grid;grid-template-columns:repeat(2,70px);gap:6px}
.b-dish .mos img{width:70px;height:70px;object-fit:cover;border-radius:16px}
.b-food{grid-column:span 2;background:linear-gradient(160deg,#e3f0d6,#cfe5bb)}.b-diet{grid-column:span 2;background:linear-gradient(160deg,#e9e0f3,#d8cbe9)}
.b-allg{grid-column:span 2;background:linear-gradient(160deg,#fbe0d6,#f4c9b9)}
.b-plan{grid-column:span 6;min-height:150px;background:linear-gradient(110deg,#0f7f6c,#2a9d8a);color:#fff;border-color:transparent}.b-plan p{color:#e6f6f2;opacity:1}.b-plan .go{background:#fff;color:#0f7f6c}
.cookbox,.thesis{display:none}
.why{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:10px 0 30px}.why div{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px}.why b{display:block}.why span{color:var(--muted);font-size:14px}
@media(max-width:820px){.bento{grid-template-columns:1fr 1fr}.b-app,.b-plan,.b-cook,.b-dish{grid-column:span 2}.b-calc,.b-food,.b-diet,.b-allg{grid-column:span 1;min-height:170px}.b-app .txt{max-width:100%}.b-app img.ph{display:none}.b-app{min-height:230px}}
@media(max-width:520px){.hero{padding:14px 0 0}.hero h1{font-size:28px}.hero p{font-size:15px;margin-top:8px;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}.bento{margin-top:16px}.bt{padding:18px}.bt h3{font-size:21px}.b-dish .mos{display:none}.b-calc,.b-food,.b-diet,.b-allg{grid-column:span 2}}
.bt.ph{isolation:isolate}
.bt.ph::after{content:"";position:absolute;top:0;right:0;bottom:0;width:62%;background:var(--bg) center/cover no-repeat;opacity:.5;
-webkit-mask-image:linear-gradient(to left,#000 15%,rgba(0,0,0,.55) 45%,transparent 92%);mask-image:linear-gradient(to left,#000 15%,rgba(0,0,0,.55) 45%,transparent 92%);z-index:-1;pointer-events:none}
.b-app.ph::after{opacity:.75;width:60%}.b-plan.ph::after{opacity:.35;width:45%}
.b-app img.ph,.b-dish.ph .mos{display:none}.b-app .more{display:block;margin:12px 0 0}.b-app .txt{max-width:62%}
@media(max-width:820px){.b-app .txt{max-width:100%}}
@media(max-width:520px){.bt{min-height:180px}.b-calc,.b-food,.b-diet,.b-allg{min-height:160px}
.bt.ph::after{width:68%;opacity:.42}.b-app.ph::after{opacity:.7;width:70%}.b-cook form{flex-direction:column}}
</style>'''


def build():
    T = json.load(open(HERE / 'home_i18n.json', encoding='utf-8'))
    langs = [l for l in ['en', 'de', 'es', 'fr', 'id', 'it', 'nl', 'pl', 'pt', 'sv', 'vi', 'tr', 'uk', 'ru', 'ar', 'he', 'hi',
                         'th', 'zh', 'ja', 'ko', 'el'] if l in T]
    cook = json.load(open(ROOT / 'dishes' / 'cook.json', encoding='utf-8'))
    dishes = {d['u']: d for d in cook['d']}
    photos = json.load(open(ROOT / 'tools' / 'dishes' / 'photos.json', encoding='utf-8'))
    CU = json.load(open(ROOT / 'tools' / 'dishes' / 'cuisines.json', encoding='utf-8'))
    n_foods = len(json.load(open(ROOT / 'tools' / 'foods' / 'foods_data.json', encoding='utf-8')))
    style = re.search(r'<link rel="stylesheet" href="/dishes/dish\.css\?v=[^"]+" />',
                      (ROOT / 'dishes' / 'index.html').read_text(encoding='utf-8')).group(0)
    fmt = lambda n: f'{n:,}'.replace(',', ' ')
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{SITE}{home_url(l)}" />' for l in langs) \
        + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}/" />'
    for lang in langs:
        t = T[lang]
        d5, fd, cl = _pre(lang, D5), _pre(lang, FOODS), _pre(lang, CALC)
        app_page = '/app/' if lang == 'en' else f'/{lang}/app/'
        tiles = [('📱', t['app'], t['app_d'], app_page),
                 ('🍽️', t['dishes'], t['dishes_d'].format(n=fmt(len(dishes))), d5 + 'dishes/'),
                 ('🧊', t['cook'], t['cook_d'], d5 + 'dishes/cook/'),
                 ('🥕', t['foods'], t['foods_d'].format(n=fmt(n_foods)), fd + 'foods/'),
                 ('🥗', t['diets'], t['diets_d'], d5 + 'guides/#diets'),
                 ('🌰', t['allergies'], t['allergies_d'], d5 + 'guides/#allergies'),
                 ('🧮', t['calcs'], t['calcs_d'], cl + 'calculators/'),
                 ('📉', t['plan'], t['plan_d'], home_url(lang) + 'weight-loss-plan/')]
        tl = ''.join(f'<a class="tile" href="{h}"><span class="ti">{e}</span><b>{esc(a)}</b><span>{esc(b)}</span></a>' for e, a, b, h in tiles)
        g = cook['g']
        chips = ''.join(f'<a href="{d5}dishes/cook/?p={k}">{esc(g[k]["n"].get(lang) or g[k]["n"].get("en") or k)}</a>' for k in CHIPS if k in g)
        cards = ''
        for s in POPULAR:
            if s in dishes and s in photos and photos[s].get('src'):
                d, ph = dishes[s], photos[s]
                dl = lang if lang in d['n'] else 'en'
                href = (home_url(dl) if dl != 'en' else '/') + f'dishes/{s}/'
                cards += (f'<a class="pcard" href="{href}"><img src="{ph["src"]}" srcset="{ph["src"]} 480w, {ph["src2x"]} 960w" '
                          f'sizes="(min-width:760px) 200px, 50vw" width="480" height="480" alt="{esc(d["n"][dl])}" loading="lazy">'
                          f'<b>{esc(d["n"][dl])}</b><span>{d["k"]} {esc(t["kcal"])}</span></a>')
        mos = ''.join(f'<img src="{photos[x]["src"]}" alt="" width="70" height="70" loading="lazy">' for x in POPULAR[:4] if x in photos and photos[x].get('src'))
        cus = ''
        for s in CUISINES:
            if s in CU:
                cl_ = lang if lang in CU[s] else 'en'
                name = CU[s][cl_]['name']
                href = (home_url(cl_) if cl_ != 'en' else '/') + f'dishes/cuisine/{s}/'
                cus += f'<a href="{href}">{CU[s].get("emoji", "")} {esc(name)}</a>'
        jsonld = json.dumps([
            {'@context': 'https://schema.org', '@type': 'WebSite', 'name': 'Me Nutrition', 'url': SITE + '/', 'inLanguage': lang,
             'description': t['meta']},
            {'@context': 'https://schema.org', '@type': 'Organization', 'name': 'Me Nutrition', 'url': SITE + '/',
             'logo': SITE + '/appicon.png', 'sameAs': ['https://apps.apple.com/app/id6767123368']}], ensure_ascii=False)
        langmenu = ('<details class="langbox"><summary aria-label="Language">' + GLOBE + lang.upper() + '</summary><div class="lm">'
                    + ''.join(f'<a href="{home_url(l)}" hreflang="{l}"{" class=\"on\"" if l == lang else ""}>{LANG_NAMES[l]}</a>' for l in langs)
                    + '</div></details>')
        page = f'''<!DOCTYPE html>
<html lang="{lang}" dir="{'rtl' if lang in RTL else 'ltr'}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="apple-itunes-app" content="app-id=6767123368, affiliate-data=pt=128869855&amp;ct=banner-home" />
<title>{esc(t['title'])}</title>
<meta name="description" content="{esc(t['meta'])}" />
<link rel="canonical" href="{SITE}{home_url(lang)}" />
{hreflang}
<meta property="og:type" content="website" />
<meta property="og:site_name" content="Me Nutrition" />
<meta property="og:title" content="{esc(t['title'])}" />
<meta property="og:description" content="{esc(t['meta'])}" />
<meta property="og:url" content="{SITE}{home_url(lang)}" />
<meta property="og:image" content="{SITE}/og-cover.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" type="image/png" href="/appicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
{style}
{CSS}
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header><div class="wrap">
  <a class="brand" href="{home_url(lang)}"><img src="/appicon.png" alt="" width="32" height="32"><span class="bn"><span class="me">Me</span><span class="bn-gap"> </span><span class="nu">Nutrition</span></span></a>
  <nav class="hnav">{langmenu}<a class="dl" href="{APP.format(lang=lang)}" target="_blank" rel="noopener">{esc(t['app'])}</a></nav>
</div></header>
{sitenav(lang)}
<main class="wrap">
<section class="hero"><h1>{esc(t['h1a'])} <em>{esc(t['h1b'])}</em></h1><p>{esc(t['lead'])}</p></section>
<section class="bento">
<div class="bt b-app ph" id="app" style="--bg:url(/assets/home/app.webp)"><a class="go" href="{app_page}" aria-label="{esc(t['app_more'])}">→</a><span class="ic">📱</span><div class="txt"><h3><a href="{app_page}" style="color:inherit;text-decoration:none">{esc(t['app_h'])}</a></h3><p>{esc(t['app_d'])}</p>
<a class="btn" href="{APP.format(lang=lang)}" target="_blank" rel="noopener">{esc(t['app_btn'])}</a><a class="more" href="{app_page}">{esc(t['app_more'])} →</a></div><img class="ph" src="/shots/lunch_intl.webp" alt="" width="170" height="340" loading="lazy"></div>
<a class="bt b-calc ph" style="--bg:url(/assets/home/calc.webp)" href="{cl}calculators/"><span class="go">→</span><span class="ic"><svg class="calc-ic" viewBox="0 0 48 48" width="38" height="38" aria-hidden="true"><rect x="8" y="3" width="32" height="42" rx="6" fill="#2F3B45"/><rect x="12" y="7" width="24" height="10" rx="2.5" fill="#CFE8E1"/><text x="33.5" y="15" font-family="Manrope,Arial,sans-serif" font-size="8" font-weight="800" fill="#2F3B45" text-anchor="end">250</text><rect x="12.0" y="21" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="18.5" y="21" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="25.0" y="21" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="31.5" y="21" width="5" height="4.2" rx="1.2" fill="#F2A541"/><rect x="12.0" y="27" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="18.5" y="27" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="25.0" y="27" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="31.5" y="27" width="5" height="4.2" rx="1.2" fill="#F2A541"/><rect x="12.0" y="33" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="18.5" y="33" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="25.0" y="33" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="31.5" y="33" width="5" height="4.2" rx="1.2" fill="#F2A541"/><rect x="12.0" y="39" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="18.5" y="39" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="25.0" y="39" width="5" height="4.2" rx="1.2" fill="#E9EEF0"/><rect x="31.5" y="39" width="5" height="4.2" rx="1.2" fill="#F2A541"/></svg></span><h3>{esc(t['calcs'])}</h3><p>{esc(t['calcs_d'])}</p></a>
<div class="bt b-cook ph" style="--bg:url(/assets/home/cook.webp)"><span class="ic">🧊</span><h3>{esc(t['cook'])}</h3><p>{esc(t['cook_p'])}</p>
<form action="{d5}dishes/cook/" method="get"><input name="q" placeholder="{esc(t['cook_ph'])}" aria-label="{esc(t['cook_h'])}"><button type="submit">{esc(t['cook_btn'])}</button></form></div>
<a class="bt b-dish ph" style="--bg:url(/assets/home/dishes.webp)" href="{d5}dishes/"><span class="go">→</span><span class="ic">🍽️</span><div class="mos">{mos}</div><h3>{esc(t['dishes'])}</h3><p>{esc(t['dishes_d'].format(n=fmt(len(dishes))))}</p></a>
<a class="bt b-food ph" style="--bg:url(/assets/guides/celery-allergy.webp)" href="{fd}foods/"><span class="go">→</span><span class="ic">🥕</span><h3>{esc(t['foods'])}</h3><p>{esc(t['foods_d'].format(n=fmt(n_foods)))}</p></a>
<a class="bt b-diet ph" style="--bg:url(/assets/guides/vegan.webp)" href="{d5}guides/#diets"><span class="go">→</span><span class="ic">🥗</span><h3>{esc(t['diets'])}</h3><p>{esc(t['diets_d'])}</p></a>
<a class="bt b-allg ph" style="--bg:url(/assets/guides/peanut-allergy.webp)" href="{d5}guides/#allergies"><span class="go">→</span><span class="ic">🌰</span><h3>{esc(t['allergies'])}</h3><p>{esc(t['allergies_d'])}</p></a>
<a class="bt b-plan ph" style="--bg:url(/shots/scale_kg.webp)" href="{home_url(lang)}weight-loss-plan/"><span class="go">→</span><span class="ic">📉</span><h3>{esc(t['plan'])}</h3><p>{esc(t['plan_d'])}</p></a>
</section>
<div class="pcs" style="margin:-14px 0 26px">{chips}</div>
<h2>{esc(t['pop_h'])}</h2><div class="pop">{cards}</div>
<h2>{esc(t['cu_h'])}</h2><div class="pcs" style="margin-bottom:30px">{cus}</div>
<div class="why"><div><b>{esc(t['t1'])}</b><span>{esc(t['t1d'])}</span></div><div><b>{esc(t['t2'])}</b><span>{esc(t['t2d'])}</span></div><div><b>{esc(t['t3'])}</b><span>{esc(t['t3d'])}</span></div></div>
</main>
<footer><div class="wrap">
  <a href="{home_url(lang)}">Me Nutrition</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a>
  <details class="langbox up"><summary aria-label="Language">{GLOBE}{LANG_NAMES[lang]}</summary><div class="lm">{''.join(f'<a href="{home_url(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs)}</div></details>
  <p class="cite">{esc(CITE.get(lang, CITE['en']))}</p>
</div></footer>
<script>document.addEventListener("click",function(e){{document.querySelectorAll(".langbox").forEach(function(d){{if(d.open&&!d.contains(e.target))d.open=false}})}});</script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "dab6447bdaac4f67b7e2016c2698b9dd"}}'></script><!-- End Cloudflare Web Analytics --><script defer src="/android.js"></script>
</body>
</html>
'''
        p = ROOT / home_url(lang).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page, encoding='utf-8')
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{SITE}{home_url(l)}"/>' for l in langs) \
        + f'\n    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}/"/>'
    import datetime
    today = datetime.date.today().isoformat()
    (ROOT / 'sitemap-home.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + ''.join(f'  <url>\n    <loc>{SITE}{home_url(l)}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>1.0</priority>{alts}\n  </url>\n' for l in langs)
        + '</urlset>\n', encoding='utf-8')
    print('home pages:', len(langs))


if __name__ == '__main__':
    build()
