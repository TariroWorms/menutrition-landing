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
              'vi': 'Tiếng Việt', 'th': 'ไทย', 'hi': 'हिन्दी', 'zh': '中文', 'ja': '日本語', 'ko': '한국어'}
EN_INGREDIENT = {'baharat': 'baharat spice mix', 'sour_cream': 'sour cream', 'caesar_dressing': 'Caesar dressing'}
SCHEMA_DIET = {'vegan': 'VeganDiet', 'vegetarian': 'VegetarianDiet', 'gluten_free': 'GlutenFreeDiet'}

esc = lambda s: html.escape(str(s), quote=True)
# visible text: brand drawn as one word, read as "Me Nutrition" (same as on the home page)
brand = lambda s: s.replace('Me Nutrition', '<span class="bn">Me<span class="bn-gap"> </span>Nutrition</span>')


def path(lang, slug=None):
    base = '/' if lang == 'en' else f'/{lang}/'
    return base + 'dishes/' + (f'{slug}/' if slug else '')


def fill(template, values):
    """{{key}} and {{ui.key}} placeholders; values are already HTML."""
    def rep(m):
        key = m.group(1)
        if key not in values:
            raise KeyError(f'template placeholder {{{{{key}}}}} has no value')
        return str(values[key])
    return re.sub(r'\{\{([\w.]+)\}\}', rep, template)


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
        'home': '/' if lang == 'en' else f'/{lang}/', 'index': path(lang), 'emoji': c['emoji'],
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
        'langs': ''.join(f'<a href="{path(l, c["slug"])}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
    }
    values.update({f'ui.{k}': esc(v) for k, v in U.items() if isinstance(v, str)})
    return fill(template, values)


def index_page(lang, items, ui, langs, db, template):
    U = ui[lang]
    cards = ''.join(
        f'<a href="{path(lang, c["slug"])}"><span class="em">{c["emoji"]}</span><div>{esc(c["i18n"][lang]["name"])}'
        f'<span>{esc(c["i18n"][lang]["origin"])} · {round(db["dishes"][c["db_key"]]["kcal"])} {esc(U["kcal"])} / 100 {esc(U["g"])}</span></div></a>'
        for c in sorted(items, key=lambda c: c['i18n'][lang]['name']))
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l)}" />' for l in langs)
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(U['index_title']),
        'description': esc(U['index_meta']), 'url': SITE + path(lang), 'hreflang': hreflang,
        'home': '/' if lang == 'en' else f'/{lang}/', 'cards': cards,
        'langs': ''.join(f'<a href="{path(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
    }
    values.update({f'ui.{k}': brand(esc(v)) for k, v in U.items() if isinstance(v, str)})
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
    NAMES.update(json.load(open(HERE / 'ingredient_names.json', encoding='utf-8'))
                 if (HERE / 'ingredient_names.json').exists() else {})
    dup = json.load(open(HERE / 'duplicates.json', encoding='utf-8'))
    contents, skipped = {}, []
    for f in sorted((HERE / 'content').glob('*.json')):
        c = json.load(open(f, encoding='utf-8'))
        if c['db_key'] not in db['dishes'] or c['db_key'] in dup or c.get('duplicate_of'):
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
