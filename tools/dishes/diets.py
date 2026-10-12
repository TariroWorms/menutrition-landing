"""Diet labels and allergens of a dish, derived by fixed rules — never by hand.

Input: one dish of the app's dish database (ingredients, allergens, macros per 100 g).
Output: a list of labels {id, status: yes|no|check, why: {...}} that the page template
turns into text with ui.json. Every label carries its reason (the ingredients that decided it),
so a reader can see why a dish is or is not vegan, gluten-free and so on.
"""
from ingredients import flags

MEAT = {'meat', 'unknown_meat', 'pork', 'beef', 'lamb', 'poultry', 'game', 'blood'}
SEA = {'fish', 'shellfish', 'mollusc'}
ANIMAL = MEAT | SEA | {'gelatin', 'unknown_animal', 'dairy', 'egg', 'honey'}

# app allergen key -> EU-14 allergen id used on the pages
DB_ALLERGEN = {'gluten': 'gluten', 'dairy': 'milk', 'eggs': 'eggs', 'egg': 'eggs', 'soy': 'soy',
               'fish': 'fish', 'nuts': 'nuts', 'peanuts': 'peanuts', 'shellfish': 'crustaceans',
               'sesame': 'sesame'}
FLAG_ALLERGEN = {'gluten': 'gluten', 'dairy': 'milk', 'egg': 'eggs', 'soy': 'soy', 'fish': 'fish',
                 'nuts': 'nuts', 'peanuts': 'peanuts', 'shellfish': 'crustaceans', 'mollusc': 'molluscs',
                 'sesame': 'sesame', 'celery': 'celery', 'mustard': 'mustard'}
EU14_ORDER = ['gluten', 'crustaceans', 'eggs', 'fish', 'peanuts', 'soy', 'milk', 'nuts', 'celery',
              'mustard', 'sesame', 'sulphites', 'lupin', 'molluscs']


def analyse(dish):
    per = {i: flags(i) for i in dish['ingredients']}
    F = set().union(set(), *per.values())
    by = lambda fl: [i for i, f in per.items() if f & fl]

    allergens = {DB_ALLERGEN[a] for a in dish['allergens'] if a in DB_ALLERGEN}
    allergens |= {FLAG_ALLERGEN[f] for f in F if f in FLAG_ALLERGEN}
    allergen_src = {a: by({f for f, v in FLAG_ALLERGEN.items() if v == a}) for a in allergens}
    alcohol = 'alcohol' in F or 'alcohol' in dish['allergens'] or 'alcohol' in dish['tags']

    labels = []

    def add(id_, status, items=(), **extra):
        labels.append({'id': id_, 'status': status, 'items': list(items), **extra})

    # plant-based
    if F & (MEAT | SEA | {'gelatin'}):
        add('vegetarian', 'no', by(MEAT | SEA | {'gelatin'}))
    elif F & {'unknown_animal'}:
        add('vegetarian', 'check', by({'unknown_animal'}))
    else:
        add('vegetarian', 'yes')
    if not F & ANIMAL:
        add('vegan', 'yes')
    elif not F & (ANIMAL - {'unknown_animal'}):
        add('vegan', 'check', by({'unknown_animal'}))
    else:
        add('vegan', 'no', by(ANIMAL - {'unknown_animal'}))

    # pork and alcohol (what halal and many other diets exclude first)
    bad = by({'pork', 'blood'})
    if bad:
        add('no_pork', 'no', bad)
    elif F & {'unknown_meat', 'gelatin'}:
        add('no_pork', 'check', by({'unknown_meat', 'gelatin'}))
    else:
        add('no_pork', 'yes', meat=bool(F & MEAT))
    if alcohol:
        add('no_alcohol', 'no', by({'alcohol'}))
    else:
        add('no_alcohol', 'yes')

    # free-from
    add('gluten_free', 'no' if 'gluten' in allergens else 'yes', allergen_src.get('gluten', []))
    add('dairy_free', 'no' if 'milk' in allergens else 'yes', allergen_src.get('milk', []))

    # macros per 100 g
    c, p, kcal = dish['carbs_g'], dish['protein_g'], dish['kcal']
    if c <= 5:
        add('keto', 'yes', carbs=c)
    elif c <= 10:
        add('low_carb', 'yes', carbs=c)
    else:
        add('keto', 'no', carbs=c)
    share = round(100 * p * 4 / kcal) if kcal else 0
    if p >= 10 and share >= 25:
        add('high_protein', 'yes', protein=p, share=share)

    return {
        'flags': F,
        'labels': labels,
        'allergens': [a for a in EU14_ORDER if a in allergens],
        'allergen_src': allergen_src,
    }
