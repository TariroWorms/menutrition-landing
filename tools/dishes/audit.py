#!/usr/bin/env python3
"""Cross-check the app's dish database against the ingredient flags.

Writes reports/dish_db_audit.md: allergens the ingredients imply but the dish lacks,
vegetarian/vegan tags that contradict the ingredients, dirty keys.
    python3 tools/dishes/audit.py [path/to/dish_database.json]
"""
import collections
import json
import sys
from dbsource import load_db
from pathlib import Path

from ingredients import flags

DB = sys.argv[1] if len(sys.argv) > 1 else '/Users/macbookpro13/Desktop/Frankly/MeNutrition/Resources/dish_database.json'
HERE = Path(__file__).resolve().parent
ANIMAL = {'meat', 'unknown_meat', 'fish', 'shellfish', 'mollusc', 'gelatin', 'blood', 'unknown_animal'}
# app allergen key -> flag; shellfish in the app covers crustaceans and molluscs
CHECK = {'gluten': {'gluten'}, 'dairy': {'dairy'}, 'eggs': {'egg'}, 'soy': {'soy'}, 'fish': {'fish'},
         'nuts': {'nuts'}, 'shellfish': {'shellfish', 'mollusc'}, 'sesame': {'sesame'},
         'peanuts': {'peanuts'}, 'alcohol': {'alcohol'}}
TITLE = {'gluten': 'глютен', 'dairy': 'молоко', 'eggs': 'яйца', 'soy': 'соя', 'fish': 'рыба', 'nuts': 'орехи',
         'shellfish': 'моллюски/ракообразные', 'sesame': 'кунжут', 'peanuts': 'арахис', 'alcohol': 'алкоголь'}


def main():
    d = load_db(DB if len(sys.argv) > 1 else None)
    rows = collections.defaultdict(list)
    for k, v in sorted(d['dishes'].items()):
        tags = set(v['tags'])
        marked = {'eggs' if a == 'egg' else a for a in v['allergens']} | (tags & {'alcohol'})
        per = {i: flags(i) for i in v['ingredients']}
        F = set().union(set(), *per.values())
        why = lambda fl: ', '.join(i for i, f in per.items() if f & fl)
        for a, fl in CHECK.items():
            if F & fl and a not in marked:
                rows[f'A. Не отмечено: {TITLE[a]}'].append(f'`{k}` — {why(fl)}')
        veg = tags & {'vegetarian', 'vegan'}
        if veg and F & ANIMAL:
            rows['B. Тег vegetarian/vegan, но в составе животное'].append(f'`{k}` ({"/".join(sorted(veg))}) — {why(ANIMAL)}')
        if 'vegan' in tags and F & {'dairy', 'egg', 'honey'}:
            rows['C. Тег vegan, но молоко/яйца/мёд'].append(f'`{k}` — {why({"dairy", "egg", "honey"})}')
        for a in v['allergens']:
            if a not in CHECK:
                rows['D. Ключи аллергенов вне списка'].append(f'`{k}` — "{a}"')
        for t in tags:
            if ' ' in t:
                rows['D. Теги с пробелом'].append(f'`{k}` — "{t}"')
    out = [f"# Сверка базы блюд MeNutrition (dish_database.json v{d['version']}, {len(d['dishes'])} блюд)", '',
           'Каждый ключ ингредиента размечен правилами (tools/dishes/ingredients.py, ветка site-langs репозитория',
           'menutrition-landing) и сравнён с полями allergens и tags. После тире — ингредиенты, из-за которых',
           'сработало правило. Проверка автоматическая, ложные срабатывания возможны: «chocolate» считается молочным,',
           'готовые карри-пасты — с креветочной пастой, «broth» — бульон неизвестного происхождения.',
           'Решение по каждому блюду за вами. Важнее всего раздел A (глютен, рыба, яйца, молоко, арахис) и B.', '']
    for key in sorted(rows):
        out += [f'## {key} — {len(rows[key])}', ''] + [f'- {x}' for x in rows[key]] + ['']
    (HERE / 'reports').mkdir(exist_ok=True)
    (HERE / 'reports' / 'dish_db_audit.md').write_text('\n'.join(out), encoding='utf-8')
    print(d['version'], {k: len(v) for k, v in sorted(rows.items())})


if __name__ == '__main__':
    main()
