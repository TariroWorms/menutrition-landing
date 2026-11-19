#!/usr/bin/env python3
"""Build dish pages: /dishes/<slug>/ (English) and /<lang>/dishes/<slug>/ for every other language.

Sources (one format for every dish):
  - the app's dish database           numbers, ingredients, allergens (never edited here)
  - content/<db_key>.json             names, origin, intro, recipe, tips, history per language
  - ui.json                           interface words per language
  - template.html / index_template.html   the page layouts — edit them and rebuild
Diet labels and allergens come from diets.py (rules over the ingredients), not from hand-written text.

    python3 tools/dishes/build_dishes.py [--db path/to/dish_database.json] [--out dir]
"""
import argparse
import hashlib
import html
import json
import re
import sys
from dbsource import load_db
from pathlib import Path

from diets import analyse
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from appstore import mid_cta   # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SITE = 'https://menutrition.app'
DB = '/Users/macbookpro13/Desktop/Frankly/MeNutrition/Resources/dish_database.json'
RTL = {'ar', 'he'}
LANG_NAMES = {'en': 'English', 'ru': 'Русский', 'de': 'Deutsch', 'es': 'Español', 'fr': 'Français',
              'it': 'Italiano', 'ar': 'العربية', 'tr': 'Türkçe', 'he': 'עברית', 'uk': 'Українська',
              'pt': 'Português', 'nl': 'Nederlands', 'pl': 'Polski', 'sv': 'Svenska', 'id': 'Indonesia',
              'vi': 'Tiếng Việt', 'th': 'ไทย', 'hi': 'हिन्दी', 'zh': '中文', 'ja': '日本語', 'ko': '한국어', 'el': 'Ελληνικά'}
EN_INGREDIENT = {'baharat': 'baharat spice mix', 'sour_cream': 'sour cream', 'caesar_dressing': 'Caesar dressing'}
SCHEMA_DIET = {'vegan': 'VeganDiet', 'vegetarian': 'VegetarianDiet', 'gluten_free': 'GlutenFreeDiet'}

esc = lambda s: html.escape(str(s), quote=True)
# visible text: brand drawn as one word, read as "Me Nutrition" (same as on the home page)
brand = lambda s: s.replace('Me Nutrition', '<span class="bn">Me<span class="bn-gap"> </span>Nutrition</span>')


def path(lang, slug=None):
    base = '/' if lang == 'en' else f'/{lang}/'
    return base + 'dishes/' + (f'{slug}/' if slug else '')


def home(lang):
    """The home page in this language, or the English one if the site has no home page in it (e.g. Greek)."""
    return f'/{lang}/' if lang != 'en' and (HERE.parent.parent / lang / 'index.html').exists() else '/'


GLOBE = ('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
         'stroke-linecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/>'
         '<path d="M3 12h18M12 3c2.5 2.6 3.8 5.7 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.7-3.8-9S9.5 5.6 12 3Z"/></svg>')


def lang_menu(lang, langs, href):
    """Header language switcher: the languages this page exists in."""
    if len(langs) < 2:
        return ''
    items = ''.join(f'<a href="{href(l)}" hreflang="{l}"{" class=\"on\"" if l == lang else ""}>{LANG_NAMES[l]}</a>' for l in langs)
    return f'<details class="langbox"><summary aria-label="Language">{GLOBE}{lang.upper()}</summary><div class="lm">{items}</div></details>'


CITE = json.load(open(Path(__file__).resolve().parent.parent / "cite.json", encoding="utf-8"))


def fill(template, values):
    """{{key}} and {{ui.key}} placeholders; values are already HTML."""
    def rep(m):
        key = m.group(1)
        if key == 'sitenav' and key not in values:
            return '\x00SNAV\x00'
        if key == 'cite' and key not in values:
            return '\x00CITE\x00'
        if key not in values:
            raise KeyError(f'template placeholder {{{{{key}}}}} has no value')
        return str(values[key])
    out = re.sub(r'\{\{([\w.]+)\}\}', rep, template)
    if '\x00SNAV\x00' in out:
        from sitenav import sitenav
        lang = (re.search(r'<html lang="([\w-]+)"', out) or [None, 'en'])[1]
        can = re.search(r'<link rel="canonical" href="https://menutrition\.app([^"]*)"', out)
        out = out.replace('\x00SNAV\x00', sitenav(lang, can.group(1) if can else ''))
    # footer: the language list becomes a compact pop-up menu (opens upward); hreflang in <head> keeps SEO
    m = re.search(r'<span class="langs">(.*?)</span>', out, re.S)
    if m and m.group(1).count('<a ') > 1:
        lang = (re.search(r'<html lang="([\w-]+)"', out) or [None, 'en'])[1]
        out = out[:m.start()] + ('<details class="langbox up"><summary aria-label="Language">' + GLOBE
                                 + LANG_NAMES.get(lang, lang) + '</summary><div class="lm">' + m.group(1) + '</div></details>') + out[m.end():]
    if '\x00CITE\x00' in out:
        lang = (re.search(r'<html lang="([\w-]+)"', out) or [None, 'en'])[1]
        out = out.replace('\x00CITE\x00', esc(CITE.get(lang, CITE['en'])))
    return out


# dish page labels / allergens -> diet & allergy guide (/guides/<slug>/), linked when the guide exists in that language
LABEL_GUIDE = {'vegetarian': 'vegetarian', 'vegan': 'vegan', 'no_pork': 'halal', 'gluten_free': 'gluten-free',
               'dairy_free': 'dairy-free', 'keto': 'keto', 'low_carb': 'low-carb', 'high_protein': 'high-protein'}
ALLERGEN_GUIDE = {'gluten': 'gluten-free', 'crustaceans': 'shellfish-allergy', 'eggs': 'egg-allergy', 'fish': 'fish-allergy',
                  'peanuts': 'peanut-allergy', 'soy': 'soy-allergy', 'milk': 'dairy-free', 'nuts': 'tree-nut-allergy',
                  'celery': 'celery-allergy', 'mustard': 'mustard-allergy', 'sesame': 'sesame-allergy',
                  'sulphites': 'sulphite-sensitivity', 'lupin': 'lupin-allergy', 'molluscs': 'mollusc-allergy'}
GUIDE_LANGS = {}   # slug -> languages it exists in, filled in main()
METHOD_LINK = {}   # filled from method.json in main()
NAMES = {}   # ingredient_names.json: {key: {lang: name}} — fills the gaps of the app's dictionary


def ingredient_name(key, lang, dictionary):
    if lang in NAMES.get(key, {}):
        return NAMES[key][lang]
    if lang != 'en' and lang in dictionary.get(key, {}):
        return dictionary[key][lang]
    return EN_INGREDIENT.get(key, key.replace('_', ' '))


def related_keys(c, contents, db, lang, n=4):
    """Hand-picked related dishes first, then the same country, then the most shared tags."""
    me = db['dishes'][c['db_key']]
    pool = [k for k, o in contents.items() if k != c['db_key'] and lang in o['i18n']]
    picked = [k for k in c.get('related', []) if k in pool]
    def score(k):
        o, d = contents[k], db['dishes'][k]
        return (bool(c.get('country')) and o.get('country') == c.get('country'),
                len(set(d['tags']) & set(me['tags'])) + len(set(d['ingredients']) & set(me['ingredients'])))
    for k in sorted(pool, key=lambda k: (score(k), k), reverse=True):
        if len(picked) >= n:
            break
        if k not in picked and score(k)[1] > 0:
            picked.append(k)
    return picked


def fmt(n):
    return f'{n:g}'


def origin_link(lang, c, t):
    """Origin text; the country part links to its cuisine page when there is one in this language."""
    cu = CUISINE_BY_COUNTRY.get(c['i18n']['en']['origin'].split('·')[0].strip())
    if not cu or lang not in CUISINE_LANGS.get(cu, ()):
        return esc(t['origin'])
    country, sep, rest = t['origin'].partition('·')
    return f'<a href="{path(lang, "cuisine/" + cu)}">{esc(country.strip())}</a>' + (f' · {esc(rest.strip())}' if sep else '')

PHOTOS = {}
VARIANT_B = {'paella', 'paella-valenciana', 'gyoza', 'panna-cotta', 'gelato', 'brownies', 'brownie'}   # Search Console: high impressions, ~0 clicks
UTM = 'utm_source=menutrition&utm_medium=referral'


def photo_url(ph, w, h=None):
    """Absolute URL of the dish photo for og:image and structured data."""
    return SITE + ph['src2x'] if ph.get('src') else unsplash_url(ph, w, h)


def thumb(c):
    """Small square dish photo for list cards; falls back to the emoji."""
    ph = PHOTOS.get(c['slug'])
    if not ph:
        return f'<span class="em">{c["emoji"]}</span>'
    src = ph['src'] if ph.get('src') else unsplash_url(ph, 112, 112)
    return f'<img class="th" src="{src}" width="56" height="56" alt="" loading="lazy" decoding="async">'


def unsplash_url(ph, w, h=None):
    """Photo hotlinked from Unsplash's CDN with its resizing parameters (the API terms require hotlinking)."""
    h = h or round(w * 3 / 4)
    return f"{ph['raw']}&w={w}&h={h}&fit=crop&crop=entropy&q=75&fm=webp&auto=format"


def photo_block(lang, c, t, U):
    ph = PHOTOS.get(c['slug'])
    if not ph:  # no honest photo of this dish: an illustration with its emoji, not a stock photo of something else
        return f'<figure class="dphoto dtile" aria-hidden="true"><span>{c["emoji"]}</span></figure>'
    if ph.get('src'):  # a photo stored on the site (Pixabay): no credit line needed
        return (f'<figure class="dphoto"><img src="{ph["src"]}" srcset="{ph["src"]} 480w, {ph["src2x"]} 960w" '
                f'sizes="(min-width:760px) 240px, (min-width:520px) 480px, 100vw" width="480" height="480" '
                f'alt="{esc(t["name"])}" fetchpriority="high" decoding="async">{cc_caption(ph)}</figure>')
    credit = U['photo_by'].format(
        author=f'<a href="{esc(ph["author_url"])}?{UTM}" rel="noopener" target="_blank">{esc(ph["author"])}</a>',
        unsplash=f'<a href="https://unsplash.com/?{UTM}" rel="noopener" target="_blank">Unsplash</a>')
    srcset = ', '.join(f'{unsplash_url(ph, w)} {w}w' for w in (400, 800, 1200))
    return (f'<figure class="dphoto"><img src="{unsplash_url(ph, 800)}" srcset="{srcset}" sizes="(min-width:760px) 240px, (min-width:520px) 480px, 100vw" '
            f'width="800" height="600" alt="{esc(t["name"])}" fetchpriority="high" decoding="async">'
            f'<figcaption>{credit}</figcaption></figure>')


def dish_page(lang, c, dish, info, ui, contents, langs, db, template):
    t = c['i18n'][lang]
    U = ui[lang]
    ing = lambda k: ingredient_name(k, lang, db['ingredients_dictionary'])
    ml = 'portion_ml' in dish
    portion = dish['portion_ml'] if ml else c['portion_g']
    kcal_p = round(dish['kcal'] * portion / 100)

    # macros: grams per serving, bar = share of calories
    kcal_from = {'protein': dish['protein_g'] * 4, 'fat': dish['fat_g'] * 9, 'carbs': dish['carbs_g'] * 4}
    total = sum(kcal_from.values()) or 1
    colors = {'protein': '#2E7A6F', 'fat': '#C9A35B', 'carbs': '#8DA7C9'}
    macros = ''.join(
        f'<div class="macro"><b>{fmt(round(dish[m + "_g"] * portion / 100))} {esc(U["g"])}</b>'
        f'<span>{esc(U[m])}</span><em>{fmt(dish[m + "_g"])} {esc(U["g"])} / 100 {esc(U["g"])}</em>'
        f'<i style="--w:{round(100 * kcal_from[m] / total)}%;--c:{colors[m]}"></i></div>'
        for m in ('protein', 'fat', 'carbs'))

    # diet labels with their reasons
    rows = []
    order = {'yes': 0, 'check': 1, 'no': 2}
    for lb in sorted(info['labels'], key=lambda l: order[l['status']]):
        names = U['lbl'][lb['id']]
        if lb['status'] not in names:
            continue
        if lb['items']:
            why = U['why']['items'].format(items=', '.join(ing(i) for i in lb['items']))
        elif lb['id'] in ('vegan',):
            why = U['why']['none_animal']
        elif lb['id'] == 'vegetarian':
            why = U['why']['none_meat']
        elif lb['id'] == 'gluten_free':
            why = U['why']['no_gluten']
        elif lb['id'] == 'dairy_free':
            why = U['why']['no_dairy']
        elif lb['id'] in ('keto', 'low_carb'):
            why = U['why']['carbs'].format(carbs=fmt(lb['carbs']))
        elif lb['id'] == 'high_protein':
            why = U['why']['protein'].format(protein=fmt(lb['protein']), share=lb['share'])
        elif lb['id'] == 'no_pork' and lb.get('meat'):
            why = U['why']['halal_note']
        else:
            why = ''
        icon = {'yes': '✓', 'no': '✕', 'check': '?'}[lb['status']]
        title = esc(names[lb['status']])
        g = LABEL_GUIDE.get(lb['id'])
        if g and lang in GUIDE_LANGS.get(g, ()):
            title = f'<a href="{gpath(lang, g)}">{title}</a>'
        rows.append(f'<div class="label {lb["status"]}"><div class="ic">{icon}</div><div>'
                    f'<b>{title}</b>' + (f'<span>{esc(why)}</span>' if why else '') + '</div></div>')

    if info['allergens']:
        allergens = (f'<p class="note">{esc(U["allergens_note"])}</p><div class="chips">'
                     + ''.join(f'<a class="chip warn" href="{gpath(lang, ALLERGEN_GUIDE[a])}">⚠ {esc(U["allergen"][a])}</a>'
                               if lang in GUIDE_LANGS.get(ALLERGEN_GUIDE.get(a), ())
                               else f'<span class="chip warn">⚠ {esc(U["allergen"][a])}</span>' for a in info['allergens'])
                     + '</div>')
    else:
        allergens = f'<p class="note">{esc(U["allergens_none"])}</p>'

    rel = [contents[k] for k in related_keys(c, contents, db, lang)]
    related = ''
    if rel:
        related = (f'<section><h2>{esc(U["related_h"])}</h2><div class="related">' + ''.join(
            f'<a href="{path(lang, r["slug"])}">{thumb(r)}<div>{esc(r["i18n"][lang]["name"])}'
            f'<span>{round(db["dishes"][r["db_key"]]["kcal"])} {esc(U["kcal"])} / 100 {esc(U["g"])}</span></div></a>'
            for r in rel) + '</div></section>')

    url = SITE + path(lang, c['slug'])
    title = U['title'].format(name=t['name'], kcal100=round(dish['kcal']))
    description = U['meta'].format(name=t['name'], kcal100=round(dish['kcal']), kcalPortion=kcal_p, portion=portion)
    if c['slug'] in VARIANT_B and 'title_b' in U:   # CTR test: no ready-made number in the snippet, a reason to click instead
        title = U['title_b'].format(name=t['name'])
        description = U['meta_b'].format(name=t['name'])
    if ml:
        description = description.replace(f'{portion} g', f'{portion} ml').replace(f'{portion} г', f'{portion} мл').replace(f'({portion} غ)', f'({portion} مل)')
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, c["slug"])}" />' for l in langs)
    hreflang += f'\n<link rel="alternate" hreflang="x-default" href="{SITE + path("en", c["slug"])}" />'
    r = t['recipe']
    diets = [f'https://schema.org/{SCHEMA_DIET[lb["id"]]}' for lb in info['labels']
             if lb['status'] == 'yes' and lb['id'] in SCHEMA_DIET]
    # Recipe rich results need a photo of the dish: pages with a photo get Recipe markup, the others a MenuItem with the nutrition facts
    # (the recipe itself stays in the visible page).
    nutrition = {'@type': 'NutritionInformation', 'servingSize': f'{portion} {"ml" if ml else "g"}',
                 'calories': f'{kcal_p} kcal',
                 'proteinContent': f'{round(dish["protein_g"] * portion / 100)} g',
                 'fatContent': f'{round(dish["fat_g"] * portion / 100)} g',
                 'carbohydrateContent': f'{round(dish["carbs_g"] * portion / 100)} g'}
    ph = PHOTOS.get(c['slug'])
    if ph:
        jsonld = {
            '@context': 'https://schema.org', '@type': 'Recipe', 'name': t['name'], 'description': t['intro'],
            'copyrightHolder': {'@type': 'Organization', 'name': 'Me Nutrition', 'url': SITE}, 'creditText': 'Me Nutrition (menutrition.app)', 'usageInfo': SITE + '/terms#citation', 
            'inLanguage': lang, 'url': url, 'recipeCuisine': t['origin'], 'recipeYield': str(r['servings']),
            'totalTime': f'PT{r["time_min"]}M', 'recipeIngredient': [x[:200] for x in r['ingredients']],
            'recipeInstructions': [{'@type': 'HowToStep', 'text': s} for s in r['steps']],
            'nutrition': nutrition, 'author': {'@type': 'Organization', 'name': 'Me Nutrition', 'url': SITE + '/'},
            'image': [photo_url(ph, 1200, 1200), photo_url(ph, 1200, 900), photo_url(ph, 1200, 675)] if not ph.get('src') else [photo_url(ph, 960)],
            'keywords': f'{t["name"]}, {t["origin"].split("·")[0].strip()}, calories',
        }
    else:
        jsonld = {'@context': 'https://schema.org', '@type': 'MenuItem', 'name': t['name'], 'description': t['intro'],
                  'inLanguage': lang, 'url': url, 'nutrition': nutrition}
    if diets:
        jsonld['suitableForDiet'] = diets

    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(title), 'description': esc(description),
        'url': url, 'hreflang': hreflang, 'jsonld': json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'),
        'home': home(lang), 'index': path(lang), 'emoji': c['emoji'],
        'photo': photo_block(lang, c, t, U), 'photo_cls': ' has-photo', 'ogimage': photo_url(PHOTOS[c['slug']], 1200, 630) if c['slug'] in PHOTOS else SITE + '/og-cover.jpg',
        'photo_preconnect': '<link rel="preconnect" href="https://images.unsplash.com" />' if c['slug'] in PHOTOS and not PHOTOS[c['slug']].get('src') else '',
        'name': esc(t['name']), 'origin': origin_link(lang, c, t), 'intro': esc(t['intro']), 'mid': mid_cta(lang, 'dish', t['name']),
        'kcal_portion': kcal_p, 'kcal100': round(dish['kcal']),
        'per_portion': esc(U['perPortionMl' if ml else 'perPortion'].format(portion=portion)), 'macros': macros,
        'labels': ''.join(rows), 'allergens': allergens,
        'ingredients': ''.join(f'<span class="chip">{esc(ing(i))}</span>' for i in dish['ingredients']),
        'servings': esc(U['servings'].format(n=r['servings'])), 'time': esc(U['time'].format(min=r['time_min'])),
        'recipe_ingredients': ''.join(f'<li>{esc(x)}</li>' for x in r['ingredients']),
        'recipe_steps': ''.join(f'<li>{esc(x)}</li>' for x in r['steps']),
        'tips': ''.join(f'<li>{esc(x)}</li>' for x in t['tips']),
        'history': esc(t['history']), 'cta_p': brand(esc(U['cta_p'].format(name=t.get('name_inline', t['name'])))),
        'related': related, 'source': brand(esc(U['source'].format(version=db['version']))),
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{path(l, c["slug"])}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: path(l, c['slug'])),
    }
    values.update({f'ui.{k}': esc(v) for k, v in U.items() if isinstance(v, str)})
    return fill(template, values)


def group_title(lang, country_en, label):
    cu = CUISINE_BY_COUNTRY.get(country_en)
    if cu and lang in CUISINE_LANGS.get(cu, ()):
        return f'<a href="{path(lang, "cuisine/" + cu)}">{esc(label)}</a>'
    return esc(label)


COUNTRY_MIN = 6      # countries with at least this many dishes get their own page; smaller ones sit on the hub
HUB_TOP, HUB_CARDS = 16, 12   # the hub shows the biggest countries with a first few dishes each
CT = {  # country page texts: title, h1, intro, "all N" link, "other countries" heading, "search results" label
    'en': ('{c}: {n} dishes with calories and macros', '{c}: dishes', 'Calories, protein, fat and carbs for {n} dishes from {c}, with recipes.',
           'All {n} dishes · {c} →', 'Other countries', 'All dishes'),
    'ru': ('{c}: {n} блюд с калориями и БЖУ', 'Блюда: {c}', 'Калории, белки, жиры и углеводы для {n} блюд: {c}, с рецептами.',
           'Все {n} блюд · {c} →', 'Другие страны', 'Все блюда'),
    'ar': ('{c}: {n} طبقًا مع السعرات الحرارية والمغذيات', 'أطباق: {c}', 'السعرات الحرارية والبروتين والدهون والكربوهيدرات لـ {n} طبقًا من {c}، مع الوصفات.',
           '{n} طبقًا · {c} ←', 'دول أخرى', 'كل الأطباق'),
    'it': ('{c}: {n} piatti con calorie e macro', 'Piatti: {c}', 'Calorie, proteine, grassi e carboidrati per {n} piatti: {c}, con le ricette.',
           'Tutti i {n} piatti · {c} →', 'Altri paesi', 'Tutti i piatti'),
    'el': ('{c}: {n} πιάτα με θερμίδες και μακροθρεπτικά', 'Πιάτα: {c}', 'Θερμίδες, πρωτεΐνη, λίπος και υδατάνθρακες για {n} πιάτα: {c}, με συνταγές.',
           'Όλα τα {n} πιάτα · {c} →', 'Άλλες χώρες', 'Όλα τα πιάτα')}
cpath = lambda lang, a: path(lang, 'country/' + a)


def index_page(lang, items, ui, langs, db, template, country=None):
    """The dishes hub: the biggest countries with a first few dishes each, a chip per country (its own page) and a search box.
    With `country` (English name): that country's page with every dish."""
    U = ui[lang]
    groups = {}
    for c in items:
        country_en = c['i18n']['en']['origin'].split('·')[0].strip() if 'en' in c['i18n'] else ''
        groups.setdefault(country_en, []).append(c)
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    label = lambda k: max((c['i18n'][lang]['origin'].split('·')[0].strip() for c in groups[k]),
                          key=[c['i18n'][lang]['origin'].split('·')[0].strip() for c in groups[k]].count)
    anchor = lambda k: re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-')
    card = lambda c: (f'<a href="{path(lang, c["slug"])}" data-k="{esc(c["db_key"].replace("_", " "))}">{thumb(c)}'
                      f'<div>{esc(c["i18n"][lang]["name"])}<span>{round(db["dishes"][c["db_key"]]["kcal"])} {esc(U["kcal"])} / 100 {esc(U["g"])}</span></div></a>')
    T = CT.get(lang, CT['en'])
    big = [k for k in order if len(groups[k]) >= COUNTRY_MIN]
    small = [k for k in order if len(groups[k]) < COUNTRY_MIN]
    photo_first = lambda c: (c['slug'] not in PHOTOS, c['i18n'][lang]['name'])
    sort_name = lambda cs: sorted(cs, key=lambda c: c['i18n'][lang]['name'])
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + (cpath(l, anchor(country)) if country else path(l))}" />' for l in langs)
    explore = ''.join(f'<a href="{href}">{esc(txt)}</a>' for href, txt in (
        (('/' if lang == 'en' else f'/{lang}/') + 'foods/', EXPLORE[lang][2]),
        (gpath(lang), EXPLORE[lang][0]), (('/' if lang == 'en' or not (ROOT / lang / 'calculators').exists() else f'/{lang}/') + 'calculators/', EXPLORE[lang][1]))
        if lang in EXPLORE)
    if country:
        n, cl = len(groups[country]), label(country)
        html_groups = (f'<section class="group"><h2 id="{anchor(country)}">{esc(cl)}<small>{n}</small></h2><div class="related">'
                       + ''.join(card(c) for c in sort_name(groups[country])) + '</div></section>')
        siblings = ''.join(f'<a href="{cpath(lang, anchor(k))}">{esc(label(k))}<small>{len(groups[k])}</small></a>' for k in big[:HUB_TOP] if k != country)
        countries = f'<a href="{path(lang)}">{esc(T[5])}</a>' + siblings
        title, desc = T[0].format(c=cl, n=n), T[2].format(c=cl, n=n)
        h1, intro = T[1].format(c=cl), T[2].format(c=cl, n=n)
        crumb = f'<a href="{path(lang)}">{esc(U["dishes"])}</a> › {esc(cl)}'
        url = SITE + cpath(lang, anchor(country))
    else:
        parts = []
        for k in big[:HUB_TOP]:
            cs = sorted(groups[k], key=photo_first)[:HUB_CARDS]
            parts.append(f'<section class="group"><h2 id="{anchor(k)}">{group_title(lang, k, label(k))}<small>{len(groups[k])}</small></h2>'
                         f'<div class="related">' + ''.join(card(c) for c in sort_name(cs)) + '</div>'
                         f'<p class="allc"><a href="{cpath(lang, anchor(k))}">{esc(T[3].format(n=len(groups[k]), c=label(k)))}</a></p></section>')
        if small:
            sm = sort_name([c for k in small for c in groups[k]])
            parts.append(f'<section class="group"><h2 id="other">{esc(T[4])}<small>{len(sm)}</small></h2><div class="related">'
                         + ''.join(card(c) for c in sm) + '</div></section>')
        html_groups = ''.join(parts)
        chip = lambda k: f'<a href="{cpath(lang, anchor(k))}">{esc(label(k))}<small>{len(groups[k])}</small></a>'
        top, rest = big[:HUB_TOP], big[HUB_TOP:]
        countries = ''.join(chip(k) for k in top)
        if rest or small:
            countries += (f'<button type="button" class="morec" aria-expanded="false" '
                          f'onclick="var r=this.nextElementSibling;r.hidden=!r.hidden;this.setAttribute(\'aria-expanded\',!r.hidden)">'
                          f'{esc(U["more_countries"])} · {len(order)}</button>'
                          f'<div class="restc" hidden>' + ''.join(chip(k) for k in sorted(rest, key=label))
                          + (f'<a href="#other">{esc(T[4])}<small>{len(small)}</small></a>' if small else '') + '</div>')
        title, desc, h1, intro = U['index_title'], U['index_meta'], U['index_h'], U['index_p']
        crumb = esc(U['dishes'])
        url = SITE + path(lang)
    values = {
        'explore': explore, 'crumb': crumb, 'findlang': lang,
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(title),
        'description': esc(desc), 'url': url, 'hreflang': hreflang,
        'home': home(lang), 'index': path(lang), 'groups': html_groups, 'countries': countries,
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{path(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, path),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values['ui.index_h'] = brand(esc(h1))
    values['ui.index_p'] = brand(esc(intro))
    return fill(template, values)


EXPLORE = {'en': ('Diets & allergies', 'Calorie & protein calculators', 'Foods: calories per 100 g'), 'ru': ('Диеты и аллергии', 'Калькуляторы калорий и белка', 'Продукты: калорийность'),
           'ar': ('الحميات والحساسية', 'حاسبات السعرات والبروتين', 'الأطعمة: السعرات الحرارية'), 'it': ('Diete e allergie', 'Calcolatori di calorie e proteine', 'Alimenti: calorie'),
           'el': ('Δίαιτες και αλλεργίες', 'Υπολογιστές θερμίδων και πρωτεΐνης', 'Τρόφιμα: θερμίδες')}   # row under the dishes index intro
METHOD = 'how-we-count'   # /dishes/how-we-count/ — how the numbers, labels and texts are made (method.json)


def method_page(lang, M, ui, langs, db, template):
    U, T = ui[lang], M[lang]
    sections = ''
    for sec in T['sections']:
        sections += f'<section><h2>{esc(sec["h"])}</h2>' + ''.join(f'<p>{brand(esc(x))}</p>' for x in sec['p'])
        if sec.get('list'):
            sections += '<ul class="mlist">' + ''.join(f'<li>{esc(x)}</li>' for x in sec['list']) + '</ul>'
        sections += '</section>'
    sections = sections.replace('support@menutrition.app', '<a href="mailto:support@menutrition.app">support@menutrition.app</a>')
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, METHOD)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(T['title']),
        'description': esc(T['meta']), 'url': SITE + path(lang, METHOD), 'hreflang': hreflang,
        'home': home(lang), 'index': path(lang), 'sections': sections,
        'updated': esc(T['updated'].format(version=db['version'])),
        'langs': ''.join(f'<a href="{path(l, METHOD)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: path(l, METHOD)),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values.update({f'm.{k}': brand(esc(v)) for k, v in T.items() if isinstance(v, str)})
    return fill(template, values)



def md(x):
    """Guide texts: **main point** -> bold, _side remark_ -> italic (escaped first)."""
    x = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc(x))
    return re.sub(r'(?<![\w/])_(.+?)_(?![\w])', r'<em>\1</em>', x)


def gpath(lang, slug=None):
    """Diet and allergy guides: /guides/<slug>/, /<lang>/guides/<slug>/."""
    return ('/' if lang == 'en' else f'/{lang}/') + 'guides/' + (f'{slug}/' if slug else '')


def guide_dishes(spec, contents, db):
    """Dishes of the database a guide links to: those that fit a diet label, or those containing an allergen."""
    out = []
    for c in contents.values():
        info = analyse(db['dishes'][c['db_key']])
        wanted = spec.get('labels') or ([{'label': spec['label'], 'status': spec['status']}] if 'label' in spec else [])
        if any(l['id'] == w['label'] and l['status'] == w['status'] for w in wanted for l in info['labels']):
            out.append(c)
        elif 'allergen' in spec and spec['allergen'] in info['allergens']:
            out.append(c)
    return out


PAGE_PHOTOS = {'guides': {}, 'cuisines': {}}


def cc_caption(ph):
    """Credit line for a Creative Commons photo stored on the site (Wikimedia Commons / Flickr via Openverse)."""
    if not ph.get('license'):
        return ''
    lic = ph['license'] if ph['license'] in ('cc0', 'pdm') else 'CC ' + ph['license'].upper() + ' ' + ph.get('license_version', '')
    return (f'<figcaption>© <a href="{esc(ph["page"])}" rel="noopener" target="_blank">{esc(ph["author"])}</a>, '
            f'<a href="{esc(ph.get("license_url", ""))}" rel="license noopener" target="_blank">{esc(lic.strip())}</a></figcaption>')


def hero_block(kind, slug, alt, emoji):
    """Wide photo at the top of a guide or cuisine page (Pixabay, stored on the site); an emoji tile where no honest photo exists."""
    ph = PAGE_PHOTOS[kind].get(slug)
    if not ph:
        return f'<figure class="ghero gtile" aria-hidden="true"><span>{emoji}</span></figure>'
    return (f'<figure class="ghero"><img src="{ph["src"]}" srcset="{ph["src"]} 640w, {ph["src2x"]} 1280w" sizes="(min-width:800px) 760px, 100vw" '
            f'width="640" height="360" alt="{esc(alt)}" fetchpriority="high" decoding="async">{cc_caption(ph)}</figure>')


def guide_page(lang, slug, G, ui, langs, contents, db, template, limit=60):
    U, T, GU, spec = ui[lang], G[slug][lang], G['_ui'][lang], G[slug]['match']
    sections = ''
    kinds, icons = G[slug].get('kinds', []), G[slug].get('icons', [])
    for i, sec in enumerate(T['sections']):
        kind = kinds[i] if i < len(kinds) else 'info'
        icon = f'<span class="gi">{icons[i]}</span>' if i < len(icons) else ''
        body = ''.join(f'<p>{brand(md(x))}</p>' for x in sec.get('p', []))
        if sec.get('list'):
            items = ''
            for x in sec['list']:
                em, _, rest = x.partition(' ')
                if len(em) <= 3 and rest:   # leading emoji of the item
                    items += f'<li><span class="ie">{em}</span><span>{md(rest)}</span></li>'
                else:
                    items += f'<li><span>{md(x)}</span></li>'
            body += f'<ul class="glist">{items}</ul>'
        sections += f'<section class="gs {kind}"><h2>{icon}{brand(esc(sec["h"]))}</h2>{body}</section>'
    found = guide_dishes(spec, contents, db)
    dl = lambda c: lang if lang in c['i18n'] else 'en'   # dish pages not yet in this language: link the English one
    # biggest cuisines first, so the first cards are familiar dishes
    size = {}
    for c in contents.values():
        k = c['i18n']['en']['origin'].split('·')[0].strip()
        size[k] = size.get(k, 0) + 1
    found.sort(key=lambda c: (dl(c) != lang, -size[c['i18n']['en']['origin'].split('·')[0].strip()], c['i18n'][dl(c)]['name']))
    head = GU['dishes_contains_h' if 'allergen' in spec else 'dishes_suits_h'].format(n=len(found))
    cards = ''.join(f'<a class="chip" href="{path(dl(c), c["slug"])}">{c["emoji"]} {esc(c["i18n"][dl(c)]["name"])}</a>'
                    for c in found[:limit])
    more = (f'<p class="note"><a href="{path(lang if sum(lang in c["i18n"] for c in contents.values()) >= 100 else "en")}">{esc(GU["dishes_more"].format(n=len(found) - limit))} →</a></p>'
            if len(found) > limit else '')
    dishes = f'<section><h2>{esc(head)}</h2><div class="chips gl">{cards}</div>{more}</section>' if found else ''
    sources = ''.join(f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(n)}</a></li>' for n, u in T['sources'])
    jsonld = json.dumps({'@context': 'https://schema.org', '@type': 'MedicalWebPage', 'name': T['title'],
                         'description': T['meta'], 'inLanguage': lang, 'url': SITE + gpath(lang, slug),
                         'lastReviewed': '2026-10-14', 'publisher': {'@type': 'Organization', 'name': 'Me Nutrition',
                                                                     'url': SITE + '/'}}, ensure_ascii=False)
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + gpath(l, slug)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(T['title']), 'description': esc(T['meta']),
        'url': SITE + gpath(lang, slug), 'hreflang': hreflang, 'home': home(lang), 'index': path(lang), 'gindex': gpath(lang),
        'sections': sections, 'dishes': dishes, 'sources': sources,
        'jsonld': f'<script type="application/ld+json">{jsonld}</script>',
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{gpath(l, slug)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: gpath(l, slug)),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values.update({f'g.{k}': esc(v) for k, v in GU.items()})
    values.update({f'm.{k}': esc(re.sub(r'\*\*|(?<![\w/])_|_(?![\w])', '', v)) for k, v in T.items() if isinstance(v, str)})
    values['emoji'] = G[slug].get('emoji', '')
    values['hero'] = hero_block('guides', slug, G[slug][lang]['name'], G[slug].get('emoji', ''))
    values['m.intro'] = brand(md(T['intro']))
    return fill(template, values)



def guides_index(lang, G, ui, langs, contents, db, template):
    U, GU = ui[lang], G['_ui'][lang]
    sections = ''
    for group in ('diets', 'allergies'):
        cards = ''
        for slug in G['_order'][group]:
            if slug not in G or lang not in G[slug]:
                continue
            n = len(guide_dishes(G[slug]['match'], contents, db))
            sub = esc(GU['n_dishes'].format(n=n)) if n else ''
            cards += (f'<a href="{gpath(lang, slug)}"><span class="em">{G[slug].get("emoji", "")}</span>'
                      f'<div>{esc(G[slug][lang]["name"])}<span>{sub}</span></div></a>')
        if cards:
            sections += f'<section id="{group}"><h2>{esc(GU[group + "_h"])}</h2><div class="related">{cards}</div></section>'
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + gpath(l)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(GU['index_title']),
        'description': esc(GU['index_meta']), 'url': SITE + gpath(lang), 'hreflang': hreflang,
        'home': home(lang), 'index': path(lang), 'sections': sections,
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{gpath(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, gpath),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values.update({f'g.{k}': esc(v) for k, v in GU.items()})
    return fill(template, values)



CUISINE_LANGS = {}   # cuisine slug -> languages, filled in main(); dish pages and the dish list link to these
CUISINE_BY_COUNTRY = {}   # English country (as in "origin") -> cuisine slug


def country_of(c):
    return c['i18n']['en']['origin'].split('·')[0].strip()


def cuisine_page(lang, slug, CU, ui, langs, contents, db, template):
    U, CL, T, meta = ui[lang], CU['_ui'][lang], CU[slug][lang], CU[slug]
    dl = lambda c: lang if lang in c['i18n'] else 'en'
    found = [c for c in contents.values() if country_of(c) == meta['match']]
    d = lambda c: db['dishes'][c['db_key']]
    card = lambda c, sub: (f'<a href="{path(dl(c), c["slug"])}">{thumb(c)}'
                           f'<div>{esc(c["i18n"][dl(c)]["name"])}<span>{sub}</span></div></a>')
    kcal = lambda c: f'{round(d(c)["kcal"])} {esc(CL["per100"])}'
    food = [c for c in found if 'drink' not in d(c)['tags']]
    meals = [c for c in food if not {'dessert', 'sweet', 'snack', 'bread'} & set(d(c)['tags'])]
    light = sorted(food, key=lambda c: d(c)['kcal'])[:8]
    heavy = sorted(meals, key=lambda c: -d(c)['kcal'])[:8]
    prot = sorted([c for c in food if any(l['id'] == 'high_protein' for l in analyse(d(c))['labels'])],
                  key=lambda c: -d(c)['protein_g'])[:8]
    lists = ''
    for h, items, sub in ((CL['lightest_h'], light, kcal), (CL['filling_h'], heavy, kcal),
                          (CL['protein_h'], prot, lambda c: f'{fmt(d(c)["protein_g"])} {esc(CL["protein_g"])}')):
        if items:
            lists += f'<section><h2>{esc(h)}</h2><div class="related">{"".join(card(c, sub(c)) for c in items)}</div></section>'
    veg = sum(any(l['id'] == 'vegetarian' and l['status'] == 'yes' for l in analyse(d(c))['labels']) for c in found)
    avg = round(sum(d(c)['kcal'] for c in found) / len(found))
    stats = (f'<div><b>{len(found)}</b><span>{esc(CL["dishes_n"])}</span></div><div><b>{avg}</b><span>{esc(CL["avg"])}</span></div>'
             f'<div><b>{round(100 * veg / len(found))}%</b><span>{esc(CL["veg"])}</span></div>')
    allc = ''.join(f'<a class="chip" href="{path(dl(c), c["slug"])}">{c["emoji"]} {esc(c["i18n"][dl(c)]["name"])}</a>'
                   for c in sorted(found, key=lambda c: c['i18n'][dl(c)]['name']))
    others = ''.join(f'<a class="chip" href="{path(lang, "cuisine/" + s)}">{CU[s]["emoji"]} {esc(CU[s][lang]["name"])}</a>'
                     for s in CU['_order'] if s != slug and lang in CU[s])
    plain = lambda x: re.sub(r'\*\*', '', x)
    jsonld = json.dumps({'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': plain(T['title']),
                         'description': plain(T['meta']).replace('{n}', str(len(found))), 'inLanguage': lang,
                         'url': SITE + path(lang, 'cuisine/' + slug)}, ensure_ascii=False)
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, "cuisine/" + slug)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(plain(T['title'])),
        'description': esc(plain(T['meta']).replace('{n}', str(len(found)))), 'url': SITE + path(lang, 'cuisine/' + slug),
        'hreflang': hreflang, 'home': home(lang), 'index': path(lang), 'jsonld': f'<script type="application/ld+json">{jsonld}</script>',
        'hero': hero_block('cuisines', slug, T['name'], meta['emoji']),
        'emoji': meta['emoji'], 'name': esc(T['name']), 'intro': brand(md(T['intro'])), 'tip': brand(md(T['tip'])),
        'stats': stats, 'lists': lists, 'all_h': esc(CL['all_h'].format(n=len(found))), 'all': allc, 'others': others,
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{path(l, "cuisine/" + slug)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: path(l, 'cuisine/' + slug)),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values.update({f'c.{k}': esc(v) for k, v in CL.items()})
    return fill(template, values)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=None)
    ap.add_argument('--out', default=str(HERE.parent.parent))
    ap.add_argument('--cook-only', action='store_true', help='build only the "What can I cook?" pages (fast)')
    ap.add_argument('--only', help='JSON list of db_keys to publish (a release batch)')
    a = ap.parse_args()
    out = Path(a.out)
    db = load_db(a.db)
    # site-side extra dishes (same format as the app database; to be handed over to the app later)
    extra = 0
    for f in sorted((HERE / 'extra' / 'db').glob('*.json')):
        e = json.load(open(f, encoding='utf-8'))
        k = e.pop('db_key', f.stem)
        if k not in db['dishes']:
            db['dishes'][k] = e
            extra += 1
    if extra:
        print('extra dishes from tools/dishes/extra/db:', extra)
    ui = json.load(open(HERE / 'ui.json', encoding='utf-8'))
    template = (HERE / 'template.html').read_text(encoding='utf-8')
    style_block = re.search(r'<style>.*?</style>', template, re.S).group(0)
    # one shared stylesheet for all dish, guide and cuisine pages instead of ~12 KB of CSS inside every page
    css = style_block[len('<style>'):-len('</style>')].strip() + '\n'
    css_v = hashlib.md5(css.encode()).hexdigest()[:8]
    (out / 'dishes').mkdir(parents=True, exist_ok=True)
    (out / 'dishes' / 'dish.css').write_text(css, encoding='utf-8')
    style = f'<link rel="stylesheet" href="/dishes/dish.css?v={css_v}" />'
    template = template.replace(style_block, style)
    index_tpl = (HERE / 'index_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    method_tpl = (HERE / 'method_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    M = json.load(open(HERE / 'method.json', encoding='utf-8'))
    G = json.load(open(HERE / 'guides.json', encoding='utf-8'))
    GUIDE_LANGS.update({k: {l for l in v if l in G['_ui'] and l in ui} for k, v in G.items() if not k.startswith('_')})
    CU = json.load(open(HERE / 'cuisines.json', encoding='utf-8'))
    CU['_order'] = [k for k in CU if not k.startswith('_')]
    CUISINE_LANGS.update({k: {l for l in CU[k] if l in CU['_ui'] and l in ui} for k in CU['_order']})
    CUISINE_BY_COUNTRY.update({CU[k]['match']: k for k in CU['_order']})
    if (HERE / 'page_photos.json').exists():
        PAGE_PHOTOS.update(json.load(open(HERE / 'page_photos.json', encoding='utf-8')))
    if (HERE / 'photos.json').exists():
        PHOTOS.update(json.load(open(HERE / 'photos.json', encoding='utf-8')))
    global METHOD_LINK
    METHOD_LINK = {l: M[l]['link'] for l in M}
    NAMES.update(json.load(open(HERE / 'ingredient_names.json', encoding='utf-8'))
                 if (HERE / 'ingredient_names.json').exists() else {})
    if (HERE / 'extra' / 'ingredient_names.json').exists():
        for k, v in json.load(open(HERE / 'extra' / 'ingredient_names.json', encoding='utf-8')).items():
            NAMES.setdefault(k, {}).update({l: t for l, t in v.items() if l not in NAMES.get(k, {})})
    dup = json.load(open(HERE / 'duplicates.json', encoding='utf-8'))
    contents, skipped = {}, []
    for f in sorted((HERE / 'content').glob('*.json')):
        c = json.load(open(f, encoding='utf-8'))
        # alcoholic drinks are not published: the site is about food
        if c['db_key'] not in db['dishes'] or c['db_key'] in dup or c.get('duplicate_of') \
                or 'alcohol' in db['dishes'][c['db_key']]['tags']:
            skipped.append(f.name)
            continue
        c['i18n'] = {l: v for l, v in c['i18n'].items() if l in ui}
        contents[c['db_key']] = c
    all_contents = dict(contents)
    if a.only:
        keep = set(json.load(open(a.only)))
        contents = {k: v for k, v in contents.items() if k in keep}
    if skipped:
        print(f'skipped {len(skipped)} (duplicates or not in the database): {", ".join(skipped[:10])}')
    langs = [l for l in ui if any(l in c['i18n'] for c in contents.values())]

    pages = []
    # "What can I cook?" — the fridge combinator
    import cook
    cdata = cook.cook_data(contents, db, PHOTOS, NAMES, country_of)
    (out / 'dishes').mkdir(exist_ok=True)
    (out / 'dishes' / 'cook.json').write_text(json.dumps(cdata, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    cook_tpl = (HERE / 'cook_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    cook_langs = [l for l in langs if l in cook.UI]

    def country_label(lang):
        lab = {}
        for c in contents.values():
            if lang in c['i18n']:
                lab.setdefault(country_of(c), {}).setdefault(c['i18n'][lang]['origin'].split('·')[0].strip(), 0)
                lab[country_of(c)][c['i18n'][lang]['origin'].split('·')[0].strip()] += 1
        return {k: max(v, key=v.get) for k, v in lab.items()}
    for lang in cook_langs:
        U = ui[lang]
        common = {'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'home': home(lang), 'index': path(lang),
                  'langs': ''.join(f'<a href="{path(l, "cook")}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in cook_langs),
                  'langmenu': lang_menu(lang, cook_langs, lambda l: path(l, 'cook'))}
        common.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
        p = out / path(lang, 'cook').strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(cook.cook_page(lang, ui, cook_langs, len(cdata['d']), cdata['g'], country_label, common, cook_tpl,
                                    fill, esc, brand, path, SITE), encoding='utf-8')
        pages.append(p)
    def common_for(lang):
        U = ui[lang]
        c = {'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'home': home(lang), 'index': path(lang),
             'langs': ''.join(f'<a href="{path(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in cook_langs),
             'langmenu': lang_menu(lang, cook_langs, path)}
        c.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
        return c
    pages += cook.with_pages(out, contents, cdata, cook_langs, cook_tpl, common_for, fill, esc, path, SITE)
    if a.cook_only:
        print('cook pages:', len(cook_langs), 'dishes:', len(cdata['d']), 'products:', len(cdata['g']))
        return
    for c in contents.values():
        dish = db['dishes'][c['db_key']]
        info = analyse(dish)
        dish_langs = [l for l in langs if l in c['i18n']]
        for lang in dish_langs:
            p = out / path(lang, c['slug']).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(dish_page(lang, c, dish, info, ui, contents, dish_langs, db, template), encoding='utf-8')
            pages.append(p)
    for lang in langs:
        p = out / path(lang).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        lang_items = [c for c in contents.values() if lang in c['i18n']]
        p.write_text(index_page(lang, lang_items, ui, langs, db, index_tpl), encoding='utf-8')
        pages.append(p)
        by_country = {}
        for c in lang_items:
            by_country.setdefault(c['i18n']['en']['origin'].split('·')[0].strip() if 'en' in c['i18n'] else '', []).append(c)
        for k, cs in by_country.items():
            if len(cs) < COUNTRY_MIN or not k:
                continue
            cp = out / cpath(lang, re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-')).strip('/') / 'index.html'
            cp.parent.mkdir(parents=True, exist_ok=True)
            cp.write_text(index_page(lang, lang_items, ui, langs, db, index_tpl, country=k), encoding='utf-8')
            pages.append(cp)
        # lean search file for the hub: [slug, name, kcal, english name]
        find = [[c['slug'], c['i18n'][lang]['name'], round(db['dishes'][c['db_key']]['kcal']), c['i18n'].get('en', {}).get('name', '')]
                for c in lang_items]
        (out / 'dishes' / f'find-{lang}.json').write_text(json.dumps(find, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    for lang in [l for l in langs if l in M]:
        p = out / path(lang, METHOD).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(method_page(lang, M, ui, [l for l in langs if l in M], db, method_tpl), encoding='utf-8')
        pages.append(p)
    guide_tpl = (HERE / 'guide_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    cu_tpl = (HERE / 'cuisine_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    for slug in CU['_order']:
        cu_langs = [l for l in langs if l in CUISINE_LANGS[slug]]
        for lang in cu_langs:
            p = out / path(lang, 'cuisine/' + slug).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(cuisine_page(lang, slug, CU, ui, cu_langs, contents, db, cu_tpl), encoding='utf-8')
            pages.append(p)
    gi_tpl = (HERE / 'guides_index_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    gi_langs = [l for l in langs if l in G['_ui'] and 'index_h' in G['_ui'][l]]
    for lang in gi_langs:
        p = out / gpath(lang).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(guides_index(lang, G, ui, gi_langs, contents, db, gi_tpl), encoding='utf-8')
        pages.append(p)
    for slug in [k for k in G if not k.startswith('_')]:
        g_langs = [l for l in langs if l in G[slug] and l in G['_ui']]
        for lang in g_langs:
            p = out / gpath(lang, slug).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(guide_page(lang, slug, G, ui, g_langs, contents, db, guide_tpl), encoding='utf-8')
            pages.append(p)
    # search index for the "write what you ate" box on the home page: every dish has numbers,
    # published dishes also have page links
    search = []
    for k, c in sorted(all_contents.items()):
        d = db['dishes'][k]
        ml = 'portion_ml' in d
        item = {'n': {l: t['name'] for l, t in c['i18n'].items()}, 'w': k.replace('_', ' ').lower(),
                'k': round(d['kcal']), 'p': d['portion_ml'] if ml else c['portion_g'], 'e': c.get('emoji', '')}
        if ml:
            item['ml'] = 1
        if k in contents:
            item['u'] = c['slug']
            item['l'] = [l for l in c['i18n'] if l in langs]
        search.append(item)
    (out / 'dishes').mkdir(exist_ok=True)
    (out / 'dishes' / 'search.json').write_text(json.dumps(search, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    urls = [SITE + '/' + str(p.parent.relative_to(out)) + '/' for p in pages]
    # a dish merged into another one: its old pages become redirects to the kept page (no 404 for indexed URLs)
    slug_of = {}
    for f in (HERE / 'content').glob('*.json'):
        cc = json.load(open(f, encoding='utf-8'))
        slug_of[cc['db_key']] = cc['slug']
    for old_key, new_key in dup.items():
        if old_key not in slug_of or new_key not in slug_of or slug_of[old_key] == slug_of[new_key]:
            continue
        for lang in ['en'] + [l for l in ui if l != 'en']:
            page = out / path(lang, slug_of[old_key]).strip('/') / 'index.html'
            if not page.exists():
                continue
            target = SITE + path(lang, slug_of[new_key])
            page.write_text(f'<!DOCTYPE html>\n<html lang="{lang}"><head><meta charset="UTF-8" /><title>Me Nutrition</title>'
                            f'<link rel="canonical" href="{target}" /><meta name="robots" content="noindex" />'
                            f'<meta http-equiv="refresh" content="0; url={target}" /></head>'
                            f'<body><a href="{target}">{target}</a></body></html>\n', encoding='utf-8')
    (out / 'sitemap-dishes.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in sorted(urls)) + '</urlset>\n', encoding='utf-8')
    print(f'db v{db["version"]}: {len(contents)} dishes × {len(langs)} languages ({", ".join(langs)}) → {len(pages)} pages')


if __name__ == '__main__':
    main()
