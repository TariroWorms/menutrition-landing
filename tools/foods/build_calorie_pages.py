#!/usr/bin/env python3
"""Short "calories of <food>" pages in Greek and Spanish for real Google queries
(αυγα θερμιδες, αμυγδαλα θερμιδες, tabla de calorias de los alimentos ...).

/el/thermides/  + /el/thermides/<food>/      /es/calorias/  + /es/calorias/<food>/
Numbers come from tools/foods/foods_data.json (USDA FoodData Central; CIQUAL rows credited
"ANSES-CIQUAL 2020, Etalab"); spanakopita from the site's dish database (typical recipe).
Writes sitemap-calories.xml. Run from the repo root after build_foods.py.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_foods as bf  # noqa: E402

esc, SITE, bd = bf.esc, bf.SITE, bf.bd
ROOT = HERE.parent.parent
APP = 'https://apps.apple.com/app/id6767123368?pt=128869855&ct=calories-{lang}-{page}&mt=8'
BASE = {'el': '/el/thermides/', 'es': '/es/calorias/'}
CALC = {'el': '/el/calculators/calorie-calculator/', 'es': '/es/calculators/calorie-calculator/'}

SRC = {
    'el': {'sr': 'USDA FoodData Central (SR Legacy)', 'fd': 'USDA FoodData Central (Foundation Foods)',
           'ciqual': 'ANSES-CIQUAL 2020, Etalab', 'dish': 'Me Nutrition: μέσος όρος τυπικής συνταγής'},
    'es': {'sr': 'USDA FoodData Central (SR Legacy)', 'fd': 'USDA FoodData Central (Foundation Foods)',
           'ciqual': 'ANSES-CIQUAL 2020, Etalab', 'dish': 'Me Nutrition: promedio de una receta típica'},
}

# ---- the food pages: variants (food key, label el, label es), a typical portion and an FAQ ----
PAGES = [
    {'id': 'egg', 'slug': {'el': 'avga', 'es': 'huevo'}, 'emoji': '🥚',
     'name': {'el': 'Αυγά', 'es': 'Huevo'},
     'h1': {'el': 'Αυγά: θερμίδες', 'es': 'Calorías del huevo'},
     'title': {'el': 'Αυγά θερμίδες: πόσες θερμίδες έχει 1 αυγό (βραστό, τηγανητό)',
               'es': 'Calorías del huevo: cuántas calorías tiene 1 huevo (cocido, frito)'},
     'portion': {'g': 50, 'el': '1 αυγό (μεγάλο, ~50 γρ. χωρίς τσόφλι)', 'es': '1 huevo (grande, ~50 g sin cáscara)'},
     'main': 'sr171287',
     'variants': [('sr171287', 'Ωμό', 'Crudo'), ('sr173424', 'Βραστό (σφιχτό)', 'Cocido (duro)'),
                  ('sr172186', 'Ποσέ', 'Escalfado'), ('sr172187', 'Στραπατσάδα / ανακατεμένο', 'Revuelto'),
                  ('sr172185', 'Ομελέτα', 'Tortilla francesa'), ('sr173423', 'Τηγανητό', 'Frito')],
     'tip': {'el': 'Το τηγάνισμα προσθέτει λάδι: ένα τηγανητό αυγό έχει περίπου 25–30 θερμίδες περισσότερες από ένα βραστό.',
             'es': 'Freír añade aceite: un huevo frito tiene unas 25–30 calorías más que uno cocido.'}},
    {'id': 'almonds', 'slug': {'el': 'amygdala', 'es': 'almendras'}, 'emoji': '🌰',
     'name': {'el': 'Αμύγδαλα', 'es': 'Almendras'},
     'h1': {'el': 'Αμύγδαλα: θερμίδες', 'es': 'Calorías de las almendras'},
     'title': {'el': 'Αμύγδαλα θερμίδες: πόσες θερμίδες έχει μια χούφτα αμύγδαλα',
               'es': 'Calorías de las almendras: cuántas calorías tiene un puñado'},
     'portion': {'g': 28, 'el': '1 χούφτα (~28 γρ., περίπου 23 αμύγδαλα)', 'es': '1 puñado (~28 g, unas 23 almendras)'},
     'main': 'fd2346393',
     'variants': [('fd2346393', 'Ωμά', 'Crudas'), ('sr170567', 'Καβουρδισμένα, χωρίς αλάτι', 'Tostadas, sin sal'),
                  ('sr168588', 'Καβουρδισμένα, με αλάτι', 'Tostadas, con sal')],
     'tip': {'el': 'Ένα αμύγδαλο έχει περίπου 7 θερμίδες. Είναι θρεπτικά, αλλά οι θερμίδες μαζεύονται γρήγορα όταν τρώγονται από τη σακούλα.',
             'es': 'Una almendra tiene unas 7 calorías. Son nutritivas, pero las calorías suben rápido si se comen directamente de la bolsa.'}},
    {'id': 'avocado', 'slug': {'el': 'avokanto', 'es': 'aguacate'}, 'emoji': '🥑',
     'name': {'el': 'Αβοκάντο', 'es': 'Aguacate'},
     'h1': {'el': 'Αβοκάντο: θερμίδες', 'es': 'Calorías del aguacate'},
     'title': {'el': 'Αβοκάντο θερμίδες: πόσες θερμίδες έχει 1 αβοκάντο',
               'es': 'Calorías del aguacate: cuántas calorías tiene 1 aguacate'},
     'portion': {'g': 136, 'el': '1 αβοκάντο (~136 γρ. σάρκα χωρίς φλούδα και κουκούτσι)',
                 'es': '1 aguacate (~136 g de pulpa, sin piel ni hueso)'},
     'main': 'sr171705',
     'variants': [('sr171705', 'Ωμό, μέσος όρος ποικιλιών', 'Crudo, promedio de variedades'),
                  ('sr171706', 'Ωμό, Hass (Καλιφόρνια)', 'Crudo, Hass (California)'),
                  ('sr171723', 'Ωμό, Φλόριντα', 'Crudo, Florida'),
                  ('ciqual13000', 'Σάρκα, ωμή (Γαλλία)', 'Pulpa, cruda (Francia)')],
     'tip': {'el': 'Μισό αβοκάντο (~68 γρ.) έχει περίπου 110 θερμίδες, κυρίως από μονοακόρεστα λιπαρά.',
             'es': 'Medio aguacate (~68 g) tiene unas 110 calorías, sobre todo de grasas monoinsaturadas.'}},
    {'id': 'banana', 'slug': {'el': 'banana', 'es': 'platano'}, 'emoji': '🍌',
     'name': {'el': 'Μπανάνα', 'es': 'Plátano'},
     'h1': {'el': 'Μπανάνα: θερμίδες', 'es': 'Calorías del plátano'},
     'title': {'el': 'Μπανάνα θερμίδες: πόσες θερμίδες έχει 1 μπανάνα',
               'es': 'Calorías del plátano (banana): cuántas calorías tiene 1 plátano'},
     'portion': {'g': 118, 'el': '1 μέτρια μπανάνα (~118 γρ. χωρίς φλούδα)', 'es': '1 plátano mediano (~118 g sin piel)'},
     'main': None,
     'variants': [(None, 'Ωμή', 'Crudo'), ('fd_overripe', 'Υπερώριμη', 'Muy maduro')],
     'tip': {'el': 'Μικρή μπανάνα (~100 γρ.) ≈ 90 θερμίδες, μεγάλη (~136 γρ.) ≈ 120 θερμίδες.',
             'es': 'Un plátano pequeño (~100 g) ≈ 90 calorías; uno grande (~136 g) ≈ 120 calorías.'}},
    {'id': 'spanakopita', 'slug': {'el': 'spanakopita'}, 'emoji': '🥧',
     'name': {'el': 'Σπανακόπιτα'},
     'h1': {'el': 'Σπανακόπιτα: θερμίδες'},
     'title': {'el': 'Σπανακόπιτα θερμίδες: πόσες θερμίδες έχει ένα κομμάτι σπανακοτυρόπιτα'},
     'portion': {'g': 150, 'el': '1 κομμάτι (~150 γρ.)'},
     'main': 'dish:spanakopita',
     'variants': [('dish:spanakopita', 'Σπανακοτυρόπιτα με φύλλο, φούρνου', '')],
     'tip': {'el': 'Οι θερμίδες αλλάζουν πολύ με το λάδι/βούτυρο στο φύλλο και την ποσότητα φέτας. Σπιτική με λίγο λάδι: λιγότερες· του φούρνου με πολύ βούτυρο: περισσότερες.'}},
]

# ---- the food table on the hub pages: (key, name el, name es, portion g, portion el, portion es) ----
TABLE = [
    ('sr171287', 'Αυγό', 'Huevo', 50, '1 αυγό', '1 huevo'),
    ('sr173420', 'Φέτα', 'Queso feta', 30, '1 φέτα 30 γρ.', '30 g'),
    ('sr170894', 'Γιαούρτι στραγγιστό 0%', 'Yogur griego 0%', 170, '1 κεσεδάκι', '1 envase'),
    ('ciqual19024', 'Γάλα πλήρες', 'Leche entera', 250, '1 ποτήρι', '1 vaso'),
    ('sr171413', 'Ελαιόλαδο', 'Aceite de oliva', 14, '1 κ. σούπας', '1 cucharada'),
    ('sr169094', 'Ελιές μαύρες', 'Aceitunas negras', 30, '10 ελιές', '10 aceitunas'),
    ('sr172688', 'Ψωμί ολικής', 'Pan integral', 30, '1 φέτα', '1 rebanada'),
    ('sr174915', 'Πίτα (αραβική)', 'Pan de pita', 60, '1 πίτα', '1 pita'),
    ('ciqual9104', 'Ρύζι βρασμένο', 'Arroz cocido', 150, '1 μερίδα', '1 ración'),
    ('sr169737', 'Μακαρόνια βρασμένα', 'Pasta cocida', 180, '1 μερίδα', '1 ración'),
    ('sr170438', 'Πατάτα βραστή', 'Papa / patata cocida', 150, '1 μέτρια', '1 mediana'),
    ('sr172421', 'Φακές βρασμένες', 'Lentejas cocidas', 200, '1 πιάτο', '1 plato'),
    ('sr173757', 'Ρεβίθια βρασμένα', 'Garbanzos cocidos', 160, '1 φλιτζάνι', '1 taza'),
    ('sr171477', 'Κοτόπουλο στήθος ψητό', 'Pechuga de pollo asada', 120, '1 μερίδα', '1 ración'),
    ('sr174032', 'Μοσχαρίσιος κιμάς 15% ψητός', 'Carne molida 15% asada', 100, '1 μπιφτέκι', '1 hamburguesa'),
    ('sr171998', 'Σολομός ψητός', 'Salmón al horno', 150, '1 φιλέτο', '1 filete'),
    ('sr170457', 'Ντομάτα', 'Tomate', 120, '1 μέτρια', '1 mediano'),
    ('sr168409', 'Αγγούρι', 'Pepino', 150, '1 μέτριο', '1 mediano'),
    ('ciqual20020', 'Κολοκυθάκι', 'Calabacín', 150, '1 μέτριο', '1 mediano'),
    ('sr170393', 'Καρότο', 'Zanahoria', 60, '1 μέτριο', '1 mediana'),
    ('sr171283', 'Σπανάκι ωμό', 'Espinaca cruda', 30, '1 φλιτζάνι', '1 taza'),
    ('sr170379', 'Μπρόκολο ωμό', 'Brócoli crudo', 90, '1 φλιτζάνι', '1 taza'),
    ('sr171688', 'Μήλο', 'Manzana', 180, '1 μέτριο', '1 mediana'),
    ('sr169097', 'Πορτοκάλι', 'Naranja', 130, '1 μέτριο', '1 mediana'),
    ('sr173944', 'Μπανάνα', 'Plátano', 118, '1 μέτρια', '1 mediano'),
    ('sr167762', 'Φράουλες', 'Fresas', 150, '1 φλιτζάνι', '1 taza'),
    ('sr167765', 'Καρπούζι', 'Sandía', 280, '1 φέτα', '1 rebanada'),
    ('sr169928', 'Ροδάκινο', 'Durazno / melocotón', 150, '1 μέτριο', '1 mediano'),
    ('sr173021', 'Σύκο', 'Higo', 50, '1 σύκο', '1 higo'),
    ('sr171705', 'Αβοκάντο', 'Aguacate', 136, '1 αβοκάντο', '1 aguacate'),
    ('fd2346393', 'Αμύγδαλα ωμά', 'Almendras crudas', 28, '1 χούφτα', '1 puñado'),
    ('sr170187', 'Καρύδια', 'Nueces', 28, '1 χούφτα', '1 puñado'),
    ('sr169655', 'Ζάχαρη', 'Azúcar', 4, '1 κ. γλυκού', '1 cucharadita'),
    ('sr169640', 'Μέλι', 'Miel', 21, '1 κ. σούπας', '1 cucharada'),
    ('sr170272', 'Μαύρη σοκολάτα 60–69%', 'Chocolate negro 60–69%', 20, '2 κομμάτια', '2 onzas'),
]

TXT = {
    'el': {
        'hub_title': 'Θερμίδες τροφίμων: πίνακας θερμίδων για 35 βασικά τρόφιμα',
        'hub_h1': 'Θερμίδες τροφίμων: πίνακας',
        'hub_desc': 'Πίνακας θερμίδων: πόσες θερμίδες έχουν αυγά, ψωμί, ρύζι, φέτα, φρούτα και ξηροί καρποί, ανά 100 γρ. και ανά συνηθισμένη μερίδα. Πηγή: USDA.',
        'hub_intro': 'Θερμίδες ανά 100 γρ. και ανά συνηθισμένη μερίδα για τα τρόφιμα που τρώμε πιο συχνά. Πατήστε ένα τρόφιμο για πρωτεΐνες, λιπαρά και υδατάνθρακες.',
        'popular': 'Συχνές ερωτήσεις θερμίδων',
        'col_food': 'Τρόφιμο', 'col_100': 'kcal / 100 γρ.', 'col_portion': 'Μερίδα', 'col_pkcal': 'kcal / μερίδα',
        'col_var': 'Είδος', 'col_p': 'Πρωτ.', 'col_f': 'Λιπ.', 'col_c': 'Υδατ.',
        'answer': '{portion}: <b>{kcal} θερμίδες</b>',
        'per100': '{kcal} kcal ανά 100 γρ. · πρωτεΐνες {p} γρ. · λιπαρά {f} γρ. · υδατάνθρακες {c} γρ.',
        'var_h': 'Θερμίδες ανά τρόπο μαγειρέματος', 'var_h1': 'Θερμίδες ανά είδος',
        'calc_h': 'Πόσες θερμίδες πρέπει να καταναλώνω την ημέρα;',
        'calc_p': 'Η ημερήσια ανάγκη εξαρτάται από φύλο, ηλικία, βάρος, ύψος και δραστηριότητα. Υπολογίστε τη δική σας σε 30 δευτερόλεπτα.',
        'calc_btn': 'Υπολογιστής θερμίδων →',
        'app_h': 'Μετρήστε θερμίδες με μια φωτογραφία',
        'app_p': 'Φωτογραφίστε το πιάτο σας ή τον κατάλογο του εστιατορίου και το Me Nutrition δείχνει θερμίδες και μακροθρεπτικά.',
        'app_btn': 'Κατεβάστε στο App Store', 'full': 'Πλήρη στοιχεία', 'all': 'Όλοι οι πίνακες θερμίδων',
        'src': 'Πηγή', 'note': 'Μέσες τιμές· η ποικιλία, το μέγεθος και το μαγείρεμα αλλάζουν τους αριθμούς. Δεν αποτελεί ιατρική συμβουλή.',
        'home': 'Αρχική', 'hub_crumb': 'Θερμίδες', 'g': 'γρ.',
        'faq_q1': 'Πόσες θερμίδες έχει {portion}?', 'faq_q2': 'Πόσες θερμίδες έχουν 100 γρ. {name}?',
    },
    'es': {
        'hub_title': 'Tabla de calorías de los alimentos: 35 alimentos básicos',
        'hub_h1': 'Tabla de calorías de los alimentos',
        'hub_desc': 'Tabla de calorías: cuántas calorías tienen el huevo, el pan, el arroz, la fruta y los frutos secos, por 100 g y por porción habitual. Fuente: USDA.',
        'hub_intro': 'Calorías por 100 g y por porción habitual de los alimentos más comunes. Toca un alimento para ver proteínas, grasas e hidratos.',
        'popular': 'Preguntas frecuentes',
        'col_food': 'Alimento', 'col_100': 'kcal / 100 g', 'col_portion': 'Porción', 'col_pkcal': 'kcal / porción',
        'col_var': 'Tipo', 'col_p': 'Prot.', 'col_f': 'Grasa', 'col_c': 'Hidr.',
        'answer': '{portion}: <b>{kcal} calorías</b>',
        'per100': '{kcal} kcal por 100 g · proteínas {p} g · grasas {f} g · hidratos {c} g',
        'var_h': 'Calorías según la preparación', 'var_h1': 'Calorías por tipo',
        'calc_h': '¿Cuántas calorías debo consumir al día?',
        'calc_p': 'Depende de tu sexo, edad, peso, estatura y actividad. Calcula las tuyas en 30 segundos.',
        'calc_btn': 'Calculadora de calorías →',
        'app_h': 'Cuenta calorías con una foto',
        'app_p': 'Haz una foto de tu plato o de la carta del restaurante y Me Nutrition te muestra calorías y macros.',
        'app_btn': 'Descargar en App Store', 'full': 'Datos completos', 'all': 'Tabla de calorías de los alimentos',
        'src': 'Fuente', 'note': 'Valores promedio; la variedad, el tamaño y la cocción cambian las cifras. No es consejo médico.',
        'home': 'Inicio', 'hub_crumb': 'Calorías', 'g': 'g',
        'faq_q1': '¿Cuántas calorías tiene {portion}?', 'faq_q2': '¿Cuántas calorías tienen 100 g de {name}?',
    },
}
FAQ_HUB = {
    'el': [('Πόσες θερμίδες πρέπει να καταναλώνω την ημέρα;',
            'Οι περισσότερες γυναίκες χρειάζονται περίπου 1.800–2.200 θερμίδες και οι περισσότεροι άντρες 2.200–2.800, ανάλογα με ηλικία, βάρος και δραστηριότητα. Ο υπολογιστής θερμίδων δίνει τον δικό σας αριθμό.'),
           ('Πού βρίσκω θερμίδες για άλλα τρόφιμα;', 'Στον κατάλογο τροφίμων υπάρχουν πάνω από 9.000 τρόφιμα με θερμίδες, πρωτεΐνες, λιπαρά και υδατάνθρακες.')],
    'es': [('¿Cuántas calorías debo consumir al día?',
            'La mayoría de las mujeres necesita unas 1.800–2.200 calorías al día y la mayoría de los hombres 2.200–2.800, según edad, peso y actividad. La calculadora de calorías te da tu número.'),
           ('¿Dónde encuentro las calorías de otros alimentos?', 'En el catálogo de alimentos hay más de 9.000 alimentos con calorías, proteínas, grasas e hidratos.')],
}


def nf(lang, x, d=0):
    return bf.nf(lang, x, d)


def main():
    F = {f['key']: f for f in json.load(open(HERE / 'foods_data.json', encoding='utf-8'))}
    S = json.load(open(HERE / 'foods_ui.json', encoding='utf-8'))
    ui = json.load(open(HERE.parent / 'dishes' / 'ui.json', encoding='utf-8'))
    ui.update(S.get('_common', {}))
    tpl = (HERE / 'template.html').read_text(encoding='utf-8')
    cssv = (ROOT / 'foods' / 'food.css').stat().st_mtime_ns % 10**8
    # food slugs as build_foods makes them, for "full data" links
    used, reserved = set(), set(S['_cats']) | {'search', 'page'}
    for f in json.load(open(HERE / 'foods_data.json', encoding='utf-8')):
        base = bf.slugify(f['names']['en'])
        if base in reserved:
            base += '-food'
        slug, i = base, 2
        while slug in used:
            slug, i = f'{base}-{i}', i + 1
        used.add(slug)
        F[f['key']]['slug'] = slug
    by_name = {f['names']['en']: f for f in F.values()}
    # keys that differ between data versions: resolve by English name
    alias = {'fd2346393': 'Almonds, whole, raw', 'sr170567': 'Almonds, dry roasted, no salt added',
             'sr168588': 'Almonds, dry roasted, with salt added', 'sr171705': 'Avocado, raw, all commercial varieties',
             'sr171706': 'Avocado, raw, California', 'sr171723': 'Avocado, raw, Florida', 'ciqual13000': 'Avocado, pulp, raw',
             'sr173944': 'Banana, raw', 'fd_overripe': 'Banana, overripe, raw', None: 'Banana, raw',
             'sr171283': 'Spinach, raw', 'sr170379': 'Broccoli, raw', 'sr171688': 'Apple, raw, with skin',
             'sr167762': 'Strawberries, raw', 'sr167765': 'Watermelon, raw', 'sr169640': 'Honey', 'sr170187': 'English walnuts',
             'sr170272': 'Dark chocolate, 60-69% cacao solids', 'sr169097': 'Orange, raw, all commercial varieties'}
    dish = json.load(open('/root/dishdb/dish_database.json', encoding='utf-8'))['dishes']['spanakopita'] \
        if Path('/root/dishdb/dish_database.json').exists() else {'kcal': 220, 'protein_g': 8.0, 'fat_g': 13.0, 'carbs_g': 18.0}

    def food(key):
        if key == 'dish:spanakopita':
            return {'kcal': dish['kcal'], 'protein': dish['protein_g'], 'fat': dish['fat_g'], 'carbs': dish['carbs_g'], 'src': 'dish',
                    'url': '/el/dishes/spanakopita/'}
        f = by_name.get(alias[key]) if key in alias else F.get(key)
        if f is None:
            raise SystemExit(f'food not found: {key}')
        return dict(f, url=None)

    B = bf.Builder(ROOT, [], S, ui, tpl, cssv)
    B.langs = ['el', 'es']
    pages = {l: [] for l in B.langs}

    def shell(lang, title, desc, url, alt, main, ld):
        html = B.shell(lang, title, desc, url, lambda l: alt.get(l, url), main, ld)
        # hreflang only for the languages this page really exists in
        import re
        html = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]+" />\n?', '', html)
        links = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + u}" />\n' for l, u in alt.items())
        return html.replace('</head>', links + '</head>', 1)

    PH = json.load(open(HERE / 'food_photos.json', encoding='utf-8'))
    DPH = json.load(open(HERE.parent / 'dishes' / 'photos.json', encoding='utf-8'))
    PKEY = {'egg': 'eggs-dairy/egg', 'almonds': 'legumes-nuts/almonds', 'avocado': 'fruits/avocado', 'banana': 'fruits/banana'}

    def pic(P, lang):
        ph = PH.get(PKEY.get(P['id'], '')) or DPH.get(P['id'] if P['id'] == 'spanakopita' else '')
        if not ph or not ph.get('src'):
            return f'<figure class="dphoto dtile" aria-hidden="true"><span>{P["emoji"]}</span></figure>'
        return (f'<figure class="dphoto"><img src="{ph["src"]}" srcset="{ph["src"]} 480w, {ph["src2x"]} 960w" '
                f'sizes="(min-width:760px) 240px, (min-width:520px) 480px, 100vw" width="480" height="480" '
                f'alt="{esc(P["name"][lang])}" fetchpriority="high" decoding="async"></figure>')

    def app_card(lang, page):
        t = TXT[lang]
        return (f'<section class="card cta"><h2>{esc(t["app_h"])}</h2><p>{esc(t["app_p"])}</p>'
                f'<a class="btn" href="{esc(APP.format(lang=lang, page=page))}" target="_blank" rel="noopener">{esc(t["app_btn"])}</a></section>')

    def calc_card(lang):
        t = TXT[lang]
        return (f'<section class="card"><h2>{esc(t["calc_h"])}</h2><p>{esc(t["calc_p"])}</p>'
                f'<p style="margin-top:10px"><a class="btn" href="{CALC[lang]}">{esc(t["calc_btn"])}</a></p></section>')

    def faq_ld(qa):
        return ('<script type="application/ld+json">' + json.dumps({'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
            {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in qa]}, ensure_ascii=False) + '</script>')

    def src_line(lang, srcs):
        t = TXT[lang]
        return f'<p class="fsrc">{esc(t["src"])}: {esc("; ".join(dict.fromkeys(SRC[lang][s] for s in srcs)))}. {esc(t["note"])}</p>'

    def full_link(lang, f):
        if f.get('url'):
            return f.get('url')
        return f'/{lang}/foods/{f["slug"]}/'

    # ---- food pages ----
    for P in PAGES:
        alt = {l: BASE[l] + s + '/' for l, s in P['slug'].items()}
        for lang in P['slug']:
            t, url = TXT[lang], alt[lang]
            m = food(P['main'] if P['main'] is not None else None)
            g = P['portion']['g']
            pk = round(m['kcal'] * g / 100)
            portion = P['portion'][lang]
            rows, srcs = '', []
            for key, lel, les in P['variants']:
                v = food(key)
                srcs.append(v['src'])
                rows += (f'<tr><td><a href="{full_link(lang, v)}">{esc(lel if lang == "el" else les)}</a></td>'
                         f'<td><b>{nf(lang, v["kcal"])}</b></td><td>{nf(lang, v["kcal"] * g / 100)}</td>'
                         f'<td>{nf(lang, v["protein"], 1)}</td><td>{nf(lang, v["fat"], 1)}</td><td>{nf(lang, v["carbs"], 1)}</td></tr>')
            name = P['name'][lang]
            desc = (f'{portion}: {pk} kcal. ' + t['per100'].format(kcal=nf(lang, m['kcal']), p=nf(lang, m['protein'], 1),
                                                                    f=nf(lang, m['fat'], 1), c=nf(lang, m['carbs'], 1)))
            qa = [(t['faq_q1'].format(portion=portion), f'{portion}: {pk} kcal.'),
                  (t['faq_q2'].format(name=name.lower()), f'{nf(lang, m["kcal"])} kcal.')]
            pcol = f'kcal / {esc(portion.split("(")[0].strip())}'
            main = f'''<nav class="crumbs"><a href="{bd.home(lang)}">{esc(t["home"])}</a> › <a href="{BASE[lang]}">{esc(t["hub_crumb"])}</a> › {esc(name)}</nav>
  <h1>{esc(P["h1"][lang])}</h1>
  <div class="dhero has-photo">{pic(P, lang)}
  <section class="card nut first" style="margin-top:20px"><div><div class="fkcal"><span class="big">{pk}</span><small>kcal</small></div>
  <div class="lbl">{esc(portion)}</div></div>
  <p class="intro" style="grid-column:1/-1;margin:14px 0 0">{esc(t["per100"].format(kcal=nf(lang, m["kcal"]), p=nf(lang, m["protein"], 1), f=nf(lang, m["fat"], 1), c=nf(lang, m["carbs"], 1)))}</p></section></div>
  <p class="intro">{t["answer"].format(portion=esc(portion), kcal=pk)}. {esc(P["tip"][lang])}</p>
  <section><h2>{esc(t["var_h"] if P["id"] == "egg" else t["var_h1"])}</h2>
  <div style="overflow-x:auto"><table class="wtab"><thead><tr><th>{esc(t["col_var"])}</th><th>{esc(t["col_100"])}</th><th>{pcol}</th><th>{esc(t["col_p"])}</th><th>{esc(t["col_f"])}</th><th>{esc(t["col_c"])}</th></tr></thead><tbody>{rows}</tbody></table></div></section>
  {calc_card(lang)}
  {app_card(lang, P["id"])}
  <p class="note" style="margin-top:16px"><a href="{BASE[lang]}">{esc(t["all"])} →</a></p>
  {src_line(lang, srcs)}'''
            ld = B.ld(lang, [(t['hub_crumb'], BASE[lang]), (name, url)]) + faq_ld(qa)
            B.write(lang, url, shell(lang, P['title'][lang], desc, url, alt, main, ld), sitemap=False)
            pages[lang].append((url, alt))

    # ---- hubs ----
    hub_alt = dict(BASE)
    for lang in B.langs:
        t = TXT[lang]
        rows, srcs = '', []
        for key, nel, nes, g, pel, pes in TABLE:
            v = food(key)
            srcs.append(v['src'])
            nm = nel if lang == 'el' else nes
            rows += (f'<tr><td><a href="{full_link(lang, v)}">{esc(nm)}</a></td><td><b>{nf(lang, v["kcal"])}</b></td>'
                     f'<td>{esc(pel if lang == "el" else pes)} ({g} {t["g"]})</td><td>{nf(lang, v["kcal"] * g / 100)}</td></tr>')
        links = ''.join(f'<a href="{BASE[lang] + P["slug"][lang]}/"><div>{P["emoji"]} {esc(P["h1"][lang])}</div></a>'
                        for P in PAGES if lang in P['slug'])
        faq = FAQ_HUB[lang]
        faq_html = ''.join(f'<details class="card" style="margin-top:10px"><summary><b>{esc(q)}</b></summary><p style="margin-top:8px">{esc(a)}</p></details>' for q, a in faq)
        main = f'''<nav class="crumbs"><a href="{bd.home(lang)}">{esc(t["home"])}</a> › {esc(t["hub_crumb"])}</nav>
  <h1>{esc(t["hub_h1"])}</h1>
  <p class="intro">{esc(t["hub_intro"])}</p>
  <section><div class="related">{links}</div></section>
  <section><div style="overflow-x:auto"><table class="wtab"><thead><tr><th>{esc(t["col_food"])}</th><th>{esc(t["col_100"])}</th><th>{esc(t["col_portion"])}</th><th>{esc(t["col_pkcal"])}</th></tr></thead><tbody>{rows}</tbody></table></div>
  <p class="note" style="margin-top:12px"><a href="/{lang}/foods/">{esc(S[lang]["foods"])} (9.000+) →</a></p></section>
  {calc_card(lang)}
  <section><h2>{esc(t["popular"])}</h2>{faq_html}</section>
  {app_card(lang, "table")}
  {src_line(lang, srcs)}'''
        ld = B.ld(lang, [(t['hub_crumb'], BASE[lang])]) + faq_ld(faq)
        B.write(lang, BASE[lang], shell(lang, t['hub_title'], t['hub_desc'], BASE[lang], hub_alt, main, ld), sitemap=False)
        pages[lang].insert(0, (BASE[lang], hub_alt))

    # ---- sitemap with hreflang ----
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for lang in B.langs:
        for url, alt in pages[lang]:
            out.append(f'  <url><loc>{SITE + url}</loc>' + ''.join(
                f'<xhtml:link rel="alternate" hreflang="{l}" href="{SITE + u}"/>' for l, u in alt.items()) + '</url>')
    out.append('</urlset>')
    (ROOT / 'sitemap-calories.xml').write_text('\n'.join(out) + '\n', encoding='utf-8')
    for lang in B.langs:
        for url, _ in pages[lang]:
            print(SITE + url)


if __name__ == '__main__':
    main()
