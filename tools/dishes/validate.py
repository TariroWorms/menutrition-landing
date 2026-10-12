#!/usr/bin/env python3
"""Check content/<dish>.json files against the format and the app's dish database.

    python3 tools/dishes/validate.py [--langs en,ar] [content/kabsa.json ...]   (no files = all)

ERROR — the page cannot be built or would be wrong (missing field, unknown db_key, no Arabic in ar).
WARN  — the recipe or tips mention something the database says the dish does not contain
        (eggs, dairy, gluten, nuts, sesame, soy, fish, shellfish, pork, alcohol). The database is the
        source of truth for diets and allergens, so the text must be changed, not the labels.
"""
import argparse
import json
import re
import sys
from dbsource import load_db
from pathlib import Path

from diets import analyse

HERE = Path(__file__).resolve().parent
DB = '/Users/macbookpro13/Desktop/Frankly/MeNutrition/Resources/dish_database.json'

# words in the English text -> flag the dish must have for the word to be allowed
LEXICON = {
    'egg': r'\beggs?\b|\byolks?\b|mayonnaise|\bmayo\b|meringue|aioli',
    'dairy': r'\bmilk\b|\bcream\b|\bbutter\b|\bcheese\b|yogh?urt|\bghee\b|parmesan|mozzarella|pecorino|feta|ricotta|paneer|labneh|kefir|buttermilk|sour cream|cr[eè]me fra[iî]che|mascarpone',
    'gluten': r'\bflour\b|\bbread\b|breadcrumbs|\bpasta\b|noodles|soy sauce|\bwheat\b|\bpita\b|semolina|couscous|bulgur|barley|\brye\b|croutons|panko|\bbeer\b',
    'peanuts': r'peanut',
    'nuts': r'almond|walnut|pistachio|cashew|hazelnut|pine nut|pecan|macadamia',
    'sesame': r'sesame|tahini',
    'soy': r'\bsoy\b|soya|tofu|\bmiso\b',
    'fish': r'\bfish\b|anchov|\btuna\b|salmon|sardine|\bcod\b|bonito|dashi',
    'shellfish': r'shrimp|prawn|\bcrab\b|lobster|crayfish|crawfish',
    'pork': r'\bpork\b|bacon|\bham\b|\blard\b|guanciale|pancetta|chorizo|prosciutto',
    'alcohol': r'\bwine\b|\bbeer\b|\brum\b|brandy|\bsake\b|mirin|vodka|cognac|whisk(e)?y|liqueur',
}
ALLOW = r'rice noodles?|rice vermicelli|glass noodles|rice paper|coconut milk|coconut cream|almond milk|oat milk|soy milk|butternut|peanut-free|nut-free|cream of tartar|fish-shaped|egg-free|dairy-free|gluten-free'
ARABIC = re.compile(r'[؀-ۿ]')


def text_of(t):
    r = t.get('recipe', {})
    return ' '.join([*r.get('ingredients', []), *r.get('steps', []), *t.get('tips', [])])


def check(path, db, langs, dup):
    errors, warns = [], []
    try:
        c = json.load(open(path, encoding='utf-8'))
    except Exception as e:
        return [f'not valid JSON: {e}'], []
    key = c.get('db_key')
    if key not in db['dishes']:
        return [f'db_key "{key}" is not in the dish database'], []
    if key in dup:
        errors.append(f'{key} is a duplicate of {dup[key]} — write only the canonical dish')
    if Path(path).stem != key:
        errors.append(f'file name must be {key}.json')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', c.get('slug', '')):
        errors.append('slug must be lowercase latin words joined by "-"')
    if not isinstance(c.get('portion_g'), int) or not 20 <= c['portion_g'] <= 1500:
        errors.append('portion_g must be an integer 20–1500')
    if not re.fullmatch(r'[A-Z]{2}|', c.get('country', '?')):
        errors.append('country must be an ISO 3166 alpha-2 code or ""')
    if not c.get('emoji'):
        errors.append('emoji missing')
    for lang in langs:
        t = c.get('i18n', {}).get(lang)
        if not t:
            errors.append(f'{lang}: missing')
            continue
        for f in ('name', 'origin', 'intro', 'history'):
            if not isinstance(t.get(f), str):
                errors.append(f'{lang}.{f} missing')
        r = t.get('recipe', {})
        if not isinstance(r.get('servings'), int) or not isinstance(r.get('time_min'), int):
            errors.append(f'{lang}.recipe.servings/time_min must be integers')
        if len(r.get('ingredients', [])) < 3 or len(r.get('steps', [])) < 2:
            errors.append(f'{lang}.recipe needs ≥3 ingredients and ≥2 steps')
        if not 2 <= len(t.get('tips', [])) <= 4:
            errors.append(f'{lang}.tips must have 2–4 items')
        if len(t.get('intro', '')) < 120:
            errors.append(f'{lang}.intro is too short (<120 chars)')
        if lang == 'ar' and not ARABIC.search(t.get('name', '') + t.get('intro', '')):
            errors.append('ar: text is not in Arabic')
    en = c.get('i18n', {}).get('en')
    if en:
        info = analyse(db['dishes'][key])
        have = set(info['flags'])
        al = {'eggs': 'egg', 'dairy': 'dairy', 'gluten': 'gluten', 'nuts': 'nuts', 'peanuts': 'peanuts',
              'sesame': 'sesame', 'soy': 'soy', 'fish': 'fish', 'shellfish': 'shellfish', 'alcohol': 'alcohol'}
        have |= {al[a] for a in db['dishes'][key]['allergens'] if a in al}
        if 'mollusc' in have:
            have.add('shellfish')
        text = re.sub(ALLOW, ' ', text_of(en).lower())
        # rice/glass/buckwheat-free noodles of the database dish are not wheat
        if any(re.search(r'rice|glass|vermicelli|sweet_potato|mung|kelp', i) for i in db['dishes'][key]['ingredients']):
            text = re.sub(r'\bnoodles\b', ' ', text)
        for flag, rx in LEXICON.items():
            m = re.search(rx, text)
            if m and flag not in have:
                warns.append(f'en text mentions "{m.group(0)}" ({flag}) but the database dish has no {flag}')
    return errors, warns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--langs', default='en,ar')
    ap.add_argument('files', nargs='*')
    a = ap.parse_args()
    db = load_db()
    dup = json.load(open(HERE / 'duplicates.json', encoding='utf-8'))
    files = a.files or sorted(str(p) for p in (HERE / 'content').glob('*.json'))
    langs = a.langs.split(',')
    bad = 0
    for f in files:
        errors, warns = check(f, db, langs, dup)
        for e in errors:
            print(f'ERROR {Path(f).name}: {e}')
        for w in warns:
            print(f'WARN  {Path(f).name}: {w}')
        bad += bool(errors)
    print(f'{len(files)} files, {bad} with errors')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
