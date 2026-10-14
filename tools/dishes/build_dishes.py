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
import html
import json
import re
from dbsource import load_db
from pathlib import Path

from diets import analyse

HERE = Path(__file__).resolve().parent
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


def fill(template, values):
    """{{key}} and {{ui.key}} placeholders; values are already HTML."""
    def rep(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f'template placeholder {{{{{key}}}}} has no value')
        return str(values[key])
    return re.sub(r'\{\{([\w.]+)\}\}', rep, template)


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
        rows.append(f'<div class="label {lb["status"]}"><div class="ic">{icon}</div><div>'
                    f'<b>{esc(names[lb["status"]])}</b>' + (f'<span>{esc(why)}</span>' if why else '') + '</div></div>')

    if info['allergens']:
        allergens = (f'<p class="note">{esc(U["allergens_note"])}</p><div class="chips">'
                     + ''.join(f'<span class="chip warn">⚠ {esc(U["allergen"][a])}</span>' for a in info['allergens'])
                     + '</div>')
    else:
        allergens = f'<p class="note">{esc(U["allergens_none"])}</p>'

    rel = [contents[k] for k in related_keys(c, contents, db, lang)]
    related = ''
    if rel:
        related = (f'<section><h2>{esc(U["related_h"])}</h2><div class="related">' + ''.join(
            f'<a href="{path(lang, r["slug"])}"><span class="em">{r["emoji"]}</span><div>{esc(r["i18n"][lang]["name"])}'
            f'<span>{round(db["dishes"][r["db_key"]]["kcal"])} {esc(U["kcal"])} / 100 {esc(U["g"])}</span></div></a>'
            for r in rel) + '</div></section>')

    url = SITE + path(lang, c['slug'])
    title = U['title'].format(name=t['name'])
    description = U['meta'].format(name=t['name'], kcal100=round(dish['kcal']), kcalPortion=kcal_p, portion=portion)
    if ml:
        description = description.replace(f'{portion} g', f'{portion} ml').replace(f'{portion} г', f'{portion} мл').replace(f'({portion} غ)', f'({portion} مل)')
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, c["slug"])}" />' for l in langs)
    hreflang += f'\n<link rel="alternate" hreflang="x-default" href="{SITE + path("en", c["slug"])}" />'
    r = t['recipe']
    diets = [f'https://schema.org/{SCHEMA_DIET[lb["id"]]}' for lb in info['labels']
             if lb['status'] == 'yes' and lb['id'] in SCHEMA_DIET]
    jsonld = {
        '@context': 'https://schema.org', '@type': 'Recipe', 'name': t['name'], 'description': t['intro'],
        'inLanguage': lang, 'url': url, 'recipeCuisine': t['origin'], 'recipeYield': str(r['servings']),
        'totalTime': f'PT{r["time_min"]}M', 'recipeIngredient': r['ingredients'],
        'recipeInstructions': [{'@type': 'HowToStep', 'text': s} for s in r['steps']],
        'nutrition': {'@type': 'NutritionInformation', 'servingSize': f'{portion} {"ml" if ml else "g"}',
                      'calories': f'{kcal_p} kcal',
                      'proteinContent': f'{round(dish["protein_g"] * portion / 100)} g',
                      'fatContent': f'{round(dish["fat_g"] * portion / 100)} g',
                      'carbohydrateContent': f'{round(dish["carbs_g"] * portion / 100)} g'},
        'author': {'@type': 'Organization', 'name': 'Me Nutrition', 'url': SITE + '/'},
    }
    if diets:
        jsonld['suitableForDiet'] = diets

    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(title), 'description': esc(description),
        'url': url, 'hreflang': hreflang, 'jsonld': json.dumps(jsonld, ensure_ascii=False).replace('</', '<\\/'),
        'home': home(lang), 'index': path(lang), 'emoji': c['emoji'],
        'name': esc(t['name']), 'origin': esc(t['origin']), 'intro': esc(t['intro']),
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


def index_page(lang, items, ui, langs, db, template):
    """All dishes grouped by country (biggest cuisines first), a country jump list and a search box."""
    U = ui[lang]
    groups = {}
    for c in items:
        country_en = c['i18n']['en']['origin'].split('·')[0].strip() if 'en' in c['i18n'] else ''
        groups.setdefault(country_en, []).append(c)
    order = sorted(groups, key=lambda k: (-len(groups[k]), k))
    label = lambda k: max((c['i18n'][lang]['origin'].split('·')[0].strip() for c in groups[k]),
                          key=[c['i18n'][lang]['origin'].split('·')[0].strip() for c in groups[k]].count)
    anchor = lambda k: re.sub(r'[^a-z0-9]+', '-', k.lower()).strip('-')
    card = lambda c: (f'<a href="{path(lang, c["slug"])}" data-k="{esc(c["db_key"].replace("_", " "))}"><span class="em">{c["emoji"]}</span>'
                      f'<div>{esc(c["i18n"][lang]["name"])}<span>{round(db["dishes"][c["db_key"]]["kcal"])} {esc(U["kcal"])} / 100 {esc(U["g"])}</span></div></a>')
    html_groups = ''.join(
        f'<section class="group"><h2 id="{anchor(k)}">{esc(label(k))}<small>{len(groups[k])}</small></h2><div class="related">'
        + ''.join(card(c) for c in sorted(groups[k], key=lambda c: c['i18n'][lang]['name'])) + '</div></section>'
        for k in order)
    chip = lambda k: f'<a href="#{anchor(k)}">{esc(label(k))}<small>{len(groups[k])}</small></a>'
    top, rest = order[:16], order[16:]
    countries = ''.join(chip(k) for k in top)
    if rest:
        countries += f'<details><summary>{esc(U["more_countries"])} · {len(order)}</summary>' + ''.join(chip(k) for k in sorted(rest, key=label)) + '</details>'
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(U['index_title']),
        'description': esc(U['index_meta']), 'url': SITE + path(lang), 'hreflang': hreflang,
        'home': home(lang), 'index': path(lang), 'groups': html_groups, 'countries': countries,
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{path(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, path),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    return fill(template, values)


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



def gpath(lang, slug=None):
    """Diet and allergy guides: /guides/<slug>/, /<lang>/guides/<slug>/."""
    return ('/' if lang == 'en' else f'/{lang}/') + 'guides/' + (f'{slug}/' if slug else '')


def guide_dishes(spec, contents, db):
    """Dishes of the database a guide links to: those that fit a diet label, or those containing an allergen."""
    out = []
    for c in contents.values():
        info = analyse(db['dishes'][c['db_key']])
        if 'label' in spec and any(l['id'] == spec['label'] and l['status'] == spec['status'] for l in info['labels']):
            out.append(c)
        elif 'allergen' in spec and spec['allergen'] in info['allergens']:
            out.append(c)
    return out


def guide_page(lang, slug, G, ui, langs, contents, db, template, limit=60):
    U, T, GU, spec = ui[lang], G[slug][lang], G['_ui'][lang], G[slug]['match']
    sections = ''
    kinds, icons = G[slug].get('kinds', []), G[slug].get('icons', [])
    for i, sec in enumerate(T['sections']):
        kind = kinds[i] if i < len(kinds) else 'info'
        icon = f'<span class="gi">{icons[i]}</span>' if i < len(icons) else ''
        body = ''.join(f'<p>{brand(esc(x))}</p>' for x in sec.get('p', []))
        if sec.get('list'):
            items = ''
            for x in sec['list']:
                em, _, rest = x.partition(' ')
                if len(em) <= 3 and rest:   # leading emoji of the item
                    items += f'<li><span class="ie">{em}</span><span>{esc(rest)}</span></li>'
                else:
                    items += f'<li><span>{esc(x)}</span></li>'
            body += f'<ul class="glist">{items}</ul>'
        sections += f'<section class="gs {kind}"><h2>{icon}{esc(sec["h"])}</h2>{body}</section>'
    found = guide_dishes(spec, contents, db)
    dl = lambda c: lang if lang in c['i18n'] else 'en'   # dish pages not yet in this language: link the English one
    # biggest cuisines first, so the first cards are familiar dishes
    size = {}
    for c in contents.values():
        k = c['i18n']['en']['origin'].split('·')[0].strip()
        size[k] = size.get(k, 0) + 1
    found.sort(key=lambda c: (dl(c) != lang, -size[c['i18n']['en']['origin'].split('·')[0].strip()], c['i18n'][dl(c)]['name']))
    head = GU['dishes_suits_h' if 'label' in spec else 'dishes_contains_h'].format(n=len(found))
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
        'url': SITE + gpath(lang, slug), 'hreflang': hreflang, 'home': home(lang), 'index': path(lang),
        'sections': sections, 'dishes': dishes, 'sources': sources,
        'jsonld': f'<script type="application/ld+json">{jsonld}</script>',
        'method': (f'<a href="{path(lang, METHOD)}">{esc(METHOD_LINK[lang])} →</a>' if lang in METHOD_LINK else ''),
        'langs': ''.join(f'<a href="{gpath(l, slug)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: gpath(l, slug)),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
    values.update({f'g.{k}': esc(v) for k, v in GU.items()})
    values.update({f'm.{k}': esc(v) for k, v in T.items() if isinstance(v, str)})
    values['emoji'] = G[slug].get('emoji', '')
    return fill(template, values)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', default=None)
    ap.add_argument('--out', default=str(HERE.parent.parent))
    ap.add_argument('--only', help='JSON list of db_keys to publish (a release batch)')
    a = ap.parse_args()
    out = Path(a.out)
    db = load_db(a.db)
    ui = json.load(open(HERE / 'ui.json', encoding='utf-8'))
    template = (HERE / 'template.html').read_text(encoding='utf-8')
    style = re.search(r'<style>.*?</style>', template, re.S).group(0)
    index_tpl = (HERE / 'index_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    method_tpl = (HERE / 'method_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    M = json.load(open(HERE / 'method.json', encoding='utf-8'))
    global METHOD_LINK
    METHOD_LINK = {l: M[l]['link'] for l in M}
    NAMES.update(json.load(open(HERE / 'ingredient_names.json', encoding='utf-8'))
                 if (HERE / 'ingredient_names.json').exists() else {})
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
        p.write_text(index_page(lang, [c for c in contents.values() if lang in c['i18n']], ui, langs, db, index_tpl),
                     encoding='utf-8')
        pages.append(p)
    for lang in [l for l in langs if l in M]:
        p = out / path(lang, METHOD).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(method_page(lang, M, ui, [l for l in langs if l in M], db, method_tpl), encoding='utf-8')
        pages.append(p)
    guide_tpl = (HERE / 'guide_template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    G = json.load(open(HERE / 'guides.json', encoding='utf-8'))
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
    (out / 'sitemap-dishes.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in sorted(urls)) + '</urlset>\n', encoding='utf-8')
    print(f'db v{db["version"]}: {len(contents)} dishes × {len(langs)} languages ({", ".join(langs)}) → {len(pages)} pages')


if __name__ == '__main__':
    main()
