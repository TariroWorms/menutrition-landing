#!/usr/bin/env python3
"""Print what the app's dish database says about dishes — for whoever writes content/<dish>.json.

    python3 tools/dishes/show.py kabsa shawarma ...
"""
import json
import sys
from pathlib import Path

from diets import analyse
from validate import DB

HERE = Path(__file__).resolve().parent
db = json.load(open(DB, encoding='utf-8'))
dup = json.load(open(HERE / 'duplicates.json', encoding='utf-8'))
for key in sys.argv[1:]:
    d = db['dishes'].get(key)
    if not d:
        print(f'## {key}: NOT IN DATABASE\n')
        continue
    info = analyse(d)
    labels = {l['id']: l['status'] for l in info['labels']}
    print(f'## {key}' + (f'  (duplicate of {dup[key]} — skip)' if key in dup else ''))
    print(json.dumps({
        'ingredients': d['ingredients'], 'allergens': d['allergens'], 'tags': d['tags'],
        'per_100g': {'kcal': d['kcal'], 'protein_g': d['protein_g'], 'fat_g': d['fat_g'], 'carbs_g': d['carbs_g']},
        'portion_ml': d.get('portion_ml'), 'cooking': d.get('cooking'), 'texture': d.get('texture'),
        'description': {l: d['description'].get(l) for l in ('en', 'ar')},
        'contains (derived)': sorted(info['flags']), 'diet labels': labels,
        'content file exists': (HERE / 'content' / f'{key}.json').exists(),
    }, ensure_ascii=False, indent=1))
    print()
