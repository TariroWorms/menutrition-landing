"""'What can I cook?' — the fridge combinator (/dishes/cook/, /ru/dishes/cook/ …).

Data (dishes/cook.json, one file for all languages): every published dish with its ingredients,
cooking method group, tastes, type, country and photo. The page filters it in the browser:
dishes that have ALL chosen products (a product also matches its variants: "chicken" matches
"chicken_thigh") and match the chosen method / taste / type / cuisine. When few dishes match,
it shows close ones: one product swapped for a similar one (buckwheat → rice), or one product missing.
"""
import json
import re

# cooking-method groups; the first rule whose word is in the db value wins
COOK_RULES = [
    ('deep_fried', ['deep', 'pressure-fried', 'double_fried']),
    ('grilled', ['grill', 'bbq', 'barbecue', 'spit', 'charcoal', 'tandoor', 'broil', 'skewer', 'flame', 'open_fire',
                 'wood_fired', 'wood_roasted', 'smoked', 'pit-roasted', 'embers', 'buried']),
    ('steamed', ['steam']),
    ('baked', ['bake', 'roast', 'gratin', 'toast', 'oven']),
    ('fried', ['fried', 'fry', 'saute', 'sear', 'griddle', 'crisp', 'wok', 'pan_cooked', 'sizzled', 'flamb']),
    ('stewed', ['braise', 'stew', 'slow', 'simmer', 'pilaf', 'dum', 'cooked_together', 'pot_']),
    ('boiled', ['boil', 'poach', 'blanch']),
    ('raw', ['raw', 'chill', 'assembled', 'toss', 'compos', 'blend', 'fresh', 'cure', 'pickl', 'cold', 'frozen',
             'churn', 'whip', 'set', 'marinat', 'ferment', 'mix', 'layered', 'rolled', 'pressed', 'chopped',
             'pounded', 'mashed', 'pureed', 'built', 'spread', 'macerat', 'soak']),
]
TASTE_RULES = [
    ('spicy', ['spicy', 'hot', 'fiery', 'peppery', 'chili']),
    ('sweet', ['sweet', 'honey', 'syrup', 'caramel', 'sugary']),
    ('sour', ['tangy', 'sour', 'zesty', 'citrus', 'tart', 'lemony']),
    ('creamy', ['creamy', 'cheesy', 'buttery', 'velvety', 'silky']),
    ('smoky', ['smoky', 'charred', 'smoked']),
    ('savory', ['savory', 'savoury', 'umami', 'salty', 'meaty', 'rich', 'hearty']),
    ('herby', ['herby', 'herbal', 'aromatic', 'fragrant', 'spiced', 'garlicky']),
    ('crispy', ['crispy', 'crunchy', 'flaky', 'crisp']),
    ('fresh', ['fresh', 'light', 'refreshing', 'bright', 'crisp-fresh']),
]
TYPE_ORDER = ['main', 'soup', 'salad', 'snack', 'breakfast', 'side', 'bread', 'dessert', 'drink']
# products that do not define a dish: hidden from the product picker
BORING = {'salt', 'water', 'oil', 'sugar', 'flour', 'spices', 'black_pepper', 'pepper', 'ice', 'vegetable_oil',
          'baking_powder', 'baking_soda', 'yeast', 'vinegar', 'stock', 'broth'}
# products that can stand in for each other (for "close matches")
SWAPS = [
    ['rice', 'buckwheat', 'bulgur', 'quinoa', 'couscous', 'freekeh', 'barley', 'millet', 'orzo'],
    ['chicken', 'turkey', 'duck', 'quail'],
    ['beef', 'lamb', 'pork', 'veal', 'goat', 'mutton'],
    ['shrimp', 'prawn', 'prawns', 'crab', 'lobster', 'squid', 'mussels', 'clams', 'scallops'],
    ['salmon', 'tuna', 'cod', 'fish', 'trout', 'sea_bass', 'mackerel', 'sardines', 'tilapia', 'hake'],
    ['potato', 'sweet_potato', 'cassava', 'taro', 'yam'],
    ['pasta', 'spaghetti', 'noodles', 'penne', 'linguine', 'tagliatelle', 'fettuccine', 'rice_noodles', 'udon'],
    ['cheese', 'feta', 'mozzarella', 'parmesan', 'halloumi', 'cheddar', 'paneer', 'ricotta'],
    ['lentils', 'chickpeas', 'beans', 'black_beans', 'kidney_beans', 'fava_beans', 'white_beans'],
    ['yogurt', 'labneh', 'sour_cream', 'kefir'],
    ['bread', 'pita', 'flatbread', 'tortilla', 'naan', 'lavash'],
    ['eggplant', 'zucchini'],
    ['spinach', 'chard', 'kale'],
    ['lemon', 'lime'],
    ['cream', 'milk', 'coconut_milk'],
]
MEDITERRANEAN = {'Italy', 'Greece', 'Spain', 'France', 'Turkey', 'Levant', 'Lebanon', 'Morocco', 'Portugal', 'Croatia',
                 'Cyprus', 'Tunisia', 'Malta', 'Israel', 'Syria', 'Egypt', 'Algeria', 'Libya', 'Albania', 'Monaco',
                 'Mediterranean', 'Eastern Mediterranean', 'Palestine', 'Sicily', 'Sardinia'}

UI = {
    'en': {
        'title': 'What can I cook? Dishes from the products you have',
        'meta': 'Pick the products in your fridge, a cooking method, a taste and a cuisine — get matching dishes from {n} recipes worldwide, with calories and macros.',
        'h1': 'What can I cook?',
        'intro': 'Choose what you have in the fridge — and how you want it: fried or baked, spicy or sweet, Italian or any cuisine. We show every dish that fits, with calories.',
        'products': 'Products you have', 'products_ph': 'Type a product: chicken, rice, eggplant…',
        'method': 'Cooking method', 'taste': 'Taste', 'type': 'Dish type', 'cuisine': 'Cuisine', 'any': 'Any',
        'popular': 'Popular', 'reset': 'Reset', 'found': 'Dishes that fit', 'none': 'No dish has all of this. Try removing a product or a filter.',
        'close': 'Close matches', 'swap': 'with {b} instead of {a}', 'missing': 'without {a}', 'more': 'Show more',
        'start': 'Pick a product or a filter to see dishes.', 'kcal': 'kcal / 100 g', 'med': 'Mediterranean',
        'm': {'fried': 'Pan-fried', 'deep_fried': 'Deep-fried', 'baked': 'Baked / roasted', 'grilled': 'Grilled / BBQ',
              'stewed': 'Stewed / braised', 'boiled': 'Boiled', 'steamed': 'Steamed', 'raw': 'Raw / no cooking'},
        't': {'spicy': 'Spicy', 'sweet': 'Sweet', 'sour': 'Sour / tangy', 'creamy': 'Creamy / cheesy', 'smoky': 'Smoky',
              'savory': 'Savory / hearty', 'herby': 'Herby / aromatic', 'crispy': 'Crispy', 'fresh': 'Fresh / light'},
        'y': {'main': 'Main dish', 'soup': 'Soup', 'salad': 'Salad', 'snack': 'Snack / starter', 'breakfast': 'Breakfast',
              'side': 'Side', 'bread': 'Bread / pastry', 'dessert': 'Dessert', 'drink': 'Drink'},
        'nav': 'What to cook',
    },
    'ru': {
        'title': 'Что приготовить из того, что есть в холодильнике',
        'meta': 'Выберите продукты из холодильника, способ приготовления, вкус и кухню — и получите подходящие блюда из {n} рецептов со всего мира с калориями и БЖУ.',
        'h1': 'Что приготовить?',
        'intro': 'Отметьте, что есть в холодильнике, и как хочется: жареное или запечённое, острое или сладкое, итальянское или любое. Покажем все подходящие блюда с калориями.',
        'products': 'Продукты, которые есть', 'products_ph': 'Введите продукт: курица, рис, баклажан…',
        'method': 'Способ приготовления', 'taste': 'Вкус', 'type': 'Тип блюда', 'cuisine': 'Кухня', 'any': 'Любая',
        'popular': 'Популярные', 'reset': 'Сбросить', 'found': 'Подходящие блюда', 'none': 'Блюд со всем сразу нет. Уберите продукт или фильтр.',
        'close': 'Похожие варианты', 'swap': '{b} вместо {a}', 'missing': 'без «{a}»', 'more': 'Показать ещё',
        'start': 'Выберите продукт или фильтр, чтобы увидеть блюда.', 'kcal': 'ккал / 100 г', 'med': 'Средиземноморская',
        'm': {'fried': 'Жареное на сковороде', 'deep_fried': 'Во фритюре', 'baked': 'Запечённое', 'grilled': 'Гриль / барбекю',
              'stewed': 'Тушёное', 'boiled': 'Варёное', 'steamed': 'На пару', 'raw': 'Сырое / без готовки'},
        't': {'spicy': 'Острое', 'sweet': 'Сладкое', 'sour': 'Кислое', 'creamy': 'Сливочное / сырное', 'smoky': 'Копчёное',
              'savory': 'Сытное', 'herby': 'Пряное / с травами', 'crispy': 'Хрустящее', 'fresh': 'Свежее / лёгкое'},
        'y': {'main': 'Основное', 'soup': 'Суп', 'salad': 'Салат', 'snack': 'Закуска', 'breakfast': 'Завтрак',
              'side': 'Гарнир', 'bread': 'Выпечка', 'dessert': 'Десерт', 'drink': 'Напиток'},
        'nav': 'Что приготовить',
    },
    'it': {
        'title': 'Cosa cucino? Piatti con gli ingredienti che hai',
        'meta': 'Scegli gli ingredienti che hai in frigo, la cottura, il gusto e la cucina: trova i piatti adatti tra {n} ricette del mondo, con calorie e macro.',
        'h1': 'Cosa cucino?',
        'intro': 'Scegli cosa hai in frigo e come lo vuoi: fritto o al forno, piccante o dolce, italiano o di qualsiasi cucina. Ti mostriamo tutti i piatti adatti, con le calorie.',
        'products': 'Ingredienti che hai', 'products_ph': 'Scrivi un ingrediente: pollo, riso, melanzana…',
        'method': 'Cottura', 'taste': 'Gusto', 'type': 'Tipo di piatto', 'cuisine': 'Cucina', 'any': 'Qualsiasi',
        'popular': 'Popolari', 'reset': 'Azzera', 'found': 'Piatti adatti', 'none': 'Nessun piatto ha tutto questo. Togli un ingrediente o un filtro.',
        'close': 'Alternative simili', 'swap': 'con {b} invece di {a}', 'missing': 'senza {a}', 'more': 'Mostra altri',
        'start': 'Scegli un ingrediente o un filtro per vedere i piatti.', 'kcal': 'kcal / 100 g', 'med': 'Mediterranea',
        'm': {'fried': 'In padella', 'deep_fried': 'Fritto', 'baked': 'Al forno', 'grilled': 'Alla griglia / barbecue',
              'stewed': 'In umido / brasato', 'boiled': 'Bollito', 'steamed': 'Al vapore', 'raw': 'Crudo / senza cottura'},
        't': {'spicy': 'Piccante', 'sweet': 'Dolce', 'sour': 'Acidulo', 'creamy': 'Cremoso / al formaggio', 'smoky': 'Affumicato',
              'savory': 'Sapido / sostanzioso', 'herby': 'Aromatico', 'crispy': 'Croccante', 'fresh': 'Fresco / leggero'},
        'y': {'main': 'Piatto principale', 'soup': 'Zuppa', 'salad': 'Insalata', 'snack': 'Antipasto / snack', 'breakfast': 'Colazione',
              'side': 'Contorno', 'bread': 'Pane / pasticceria', 'dessert': 'Dolce', 'drink': 'Bevanda'},
        'nav': 'Cosa cucinare',
    },
    'el': {
        'title': 'Τι να μαγειρέψω; Πιάτα με ό,τι έχεις στο ψυγείο',
        'meta': 'Διάλεξε τα υλικά που έχεις, τρόπο μαγειρέματος, γεύση και κουζίνα και βρες πιάτα από {n} συνταγές απ’ όλο τον κόσμο, με θερμίδες και μακροθρεπτικά.',
        'h1': 'Τι να μαγειρέψω;',
        'intro': 'Διάλεξε τι έχεις στο ψυγείο και πώς το θέλεις: τηγανητό ή ψητό, πικάντικο ή γλυκό, ιταλικό ή οποιαδήποτε κουζίνα. Σου δείχνουμε όλα τα πιάτα που ταιριάζουν, με θερμίδες.',
        'products': 'Υλικά που έχεις', 'products_ph': 'Γράψε ένα υλικό: κοτόπουλο, ρύζι, μελιτζάνα…',
        'method': 'Τρόπος μαγειρέματος', 'taste': 'Γεύση', 'type': 'Είδος πιάτου', 'cuisine': 'Κουζίνα', 'any': 'Οποιαδήποτε',
        'popular': 'Δημοφιλή', 'reset': 'Καθαρισμός', 'found': 'Πιάτα που ταιριάζουν', 'none': 'Κανένα πιάτο δεν τα έχει όλα. Αφαίρεσε ένα υλικό ή φίλτρο.',
        'close': 'Παρόμοιες επιλογές', 'swap': 'με {b} αντί για {a}', 'missing': 'χωρίς {a}', 'more': 'Περισσότερα',
        'start': 'Διάλεξε ένα υλικό ή φίλτρο για να δεις πιάτα.', 'kcal': 'kcal / 100 g', 'med': 'Μεσογειακή',
        'm': {'fried': 'Τηγανητό στο τηγάνι', 'deep_fried': 'Τηγανητό σε βαθύ λάδι', 'baked': 'Στο φούρνο', 'grilled': 'Σχάρα / μπάρμπεκιου',
              'stewed': 'Κατσαρόλας / μαγειρευτό', 'boiled': 'Βραστό', 'steamed': 'Στον ατμό', 'raw': 'Ωμό / χωρίς μαγείρεμα'},
        't': {'spicy': 'Πικάντικο', 'sweet': 'Γλυκό', 'sour': 'Ξινό', 'creamy': 'Κρεμώδες / με τυρί', 'smoky': 'Καπνιστό',
              'savory': 'Αλμυρό / χορταστικό', 'herby': 'Αρωματικό', 'crispy': 'Τραγανό', 'fresh': 'Δροσερό / ελαφρύ'},
        'y': {'main': 'Κυρίως πιάτο', 'soup': 'Σούπα', 'salad': 'Σαλάτα', 'snack': 'Ορεκτικό / σνακ', 'breakfast': 'Πρωινό',
              'side': 'Συνοδευτικό', 'bread': 'Ψωμί / ζύμες', 'dessert': 'Επιδόρπιο', 'drink': 'Ρόφημα'},
        'nav': 'Τι να μαγειρέψω',
    },
    'ar': {
        'title': 'ماذا أطبخ؟ أطباق من المكونات الموجودة لديك',
        'meta': 'اختر المكونات الموجودة في ثلاجتك وطريقة الطهي والطعم والمطبخ، واحصل على أطباق مناسبة من {n} وصفة من حول العالم مع السعرات والعناصر الغذائية.',
        'h1': 'ماذا أطبخ؟',
        'intro': 'اختر ما لديك في الثلاجة وكيف تريده: مقلي أو مشوي في الفرن، حار أو حلو، إيطالي أو من أي مطبخ. نعرض لك كل الأطباق المناسبة مع السعرات.',
        'products': 'المكونات المتوفرة', 'products_ph': 'اكتب مكوّنًا: دجاج، أرز، باذنجان…',
        'method': 'طريقة الطهي', 'taste': 'الطعم', 'type': 'نوع الطبق', 'cuisine': 'المطبخ', 'any': 'أي مطبخ',
        'popular': 'الأكثر استخدامًا', 'reset': 'مسح', 'found': 'الأطباق المناسبة', 'none': 'لا يوجد طبق يجمع كل ذلك. أزل مكوّنًا أو فلترًا.',
        'close': 'خيارات قريبة', 'swap': 'مع {b} بدل {a}', 'missing': 'بدون {a}', 'more': 'عرض المزيد',
        'start': 'اختر مكوّنًا أو فلترًا لعرض الأطباق.', 'kcal': 'سعرة / 100 غ', 'med': 'متوسطي',
        'm': {'fried': 'مقلي في المقلاة', 'deep_fried': 'مقلي في زيت غزير', 'baked': 'في الفرن', 'grilled': 'مشوي / باربكيو',
              'stewed': 'مطهو ببطء', 'boiled': 'مسلوق', 'steamed': 'على البخار', 'raw': 'نيء / بدون طهي'},
        't': {'spicy': 'حار', 'sweet': 'حلو', 'sour': 'حامض', 'creamy': 'كريمي / بالجبن', 'smoky': 'مدخّن',
              'savory': 'مالح / مشبع', 'herby': 'بالأعشاب / عطري', 'crispy': 'مقرمش', 'fresh': 'منعش / خفيف'},
        'y': {'main': 'طبق رئيسي', 'soup': 'شوربة', 'salad': 'سلطة', 'snack': 'مقبلات / وجبة خفيفة', 'breakfast': 'فطور',
              'side': 'طبق جانبي', 'bread': 'خبز / معجنات', 'dessert': 'حلوى', 'drink': 'مشروب'},
        'nav': 'ماذا أطبخ',
    },
}


def _group(value, rules, default=None):
    v = (value or '').lower()
    for name, words in rules:
        if any(w in v for w in words):
            return name
    return default


def _list(x):
    if isinstance(x, list):
        return x
    try:
        import ast
        return list(ast.literal_eval(x or '[]'))
    except Exception:
        return []


def dish_type(tags):
    t = set(tags)
    for name, keys in (('drink', {'drink'}), ('dessert', {'dessert', 'sweet'}), ('soup', {'soup'}), ('salad', {'salad'}),
                       ('breakfast', {'breakfast'}), ('bread', {'bread'}), ('side', {'side'}),
                       ('snack', {'snack', 'appetizer', 'street_food'})):
        if t & keys:
            return name
    return 'main'


def cook_data(contents, db, photos, names, country_of):
    dishes, used = [], {}
    for k, c in contents.items():
        d = db['dishes'][k]
        ing = [i for i in _list(d['ingredients'])]
        tastes = []
        tex = d.get('texture', '')
        for name, words in TASTE_RULES:
            if any(w in str(tex).lower() for w in words) and name not in tastes:
                tastes.append(name)
        if str(d.get('spicy')) == 'True' and 'spicy' not in tastes:
            tastes.insert(0, 'spicy')
        ph = photos.get(c['slug'], {})
        src = ph.get('src') or (f"{ph['raw']}&w=112&h=112&fit=crop&q=70&fm=webp" if ph.get('raw') else '')
        dishes.append({'u': c['slug'], 'n': {l: t['name'] for l, t in c['i18n'].items()}, 'i': ing,
                       'm': _group(d.get('cooking'), COOK_RULES), 't': tastes, 'y': dish_type(_list(d['tags'])),
                       'c': country_of(c), 'k': round(d['kcal']), 'p': src, 'e': c.get('emoji', '')})
        for i in ing:
            used[i] = used.get(i, 0) + 1
    ingredients = {i: {'n': names.get(i, {}), 'c': n} for i, n in used.items() if i not in BORING}
    return {'d': dishes, 'g': ingredients, 's': SWAPS, 'med': sorted(MEDITERRANEAN)}


COOK_JS = r"""
(function(){
var L=document.documentElement.lang, U=JSON.parse(document.getElementById('cook-ui').textContent), D, sel=[], f={m:'',t:'',y:'',c:''};
var $=function(i){return document.getElementById(i)}, box=$('chips'), inp=$('prod'), sug=$('sug'), out=$('res'), close=$('close');
var nm=function(k){var g=D.g[k];return (g&&g.n&&(g.n[L]||g.n.en))||k.replace(/_/g,' ')};
var norm=function(s){return (s||'').toLowerCase().normalize('NFD').replace(/[̀-ًͯ-ْ]/g,'')};
var has=function(d,k){var w='_'+k+'_';return d.i.some(function(x){return x===k||('_'+x+'_').indexOf(w)>=0})};
var swapOf=function(k){for(var i=0;i<D.s.length;i++)if(D.s[i].indexOf(k)>=0)return D.s[i].filter(function(x){return x!==k});return []};
var esc=function(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})};
var href=function(u){return (L==='en'?'/':'/'+L+'/')+'dishes/'+u+'/'};
var card=function(d,note){var n=d.n[L]||d.n.en;return '<a href="'+href(d.u)+'">'+(d.p?'<img class="th" src="'+d.p+'" width="56" height="56" alt="" loading="lazy">':'<span class="em">'+d.e+'</span>')+'<div>'+esc(n)+'<span>'+d.k+' '+esc(U.kcal)+(note?' · '+esc(note):'')+'</span></div></a>'};
var okF=function(d){return (!f.m||d.m===f.m)&&(!f.t||d.t.indexOf(f.t)>=0)&&(!f.y||d.y===f.y)&&(!f.c||(f.c==='__med'?D.med.indexOf(d.c)>=0:d.c===f.c))};
function render(){
  [].forEach.call(document.querySelectorAll('#pop button'),function(b){b.classList.toggle('on',sel.indexOf(b.dataset.k)>=0)});
  box.innerHTML=sel.map(function(k){return '<button type="button" class="pc on" data-k="'+k+'">'+esc(nm(k))+' ✕</button>'}).join('');
  var st=new URLSearchParams();if(sel.length)st.set('p',sel.join(','));['m','t','y','c'].forEach(function(x){if(f[x])st.set(x,f[x])});
  history.replaceState(null,'',location.pathname+(st.toString()?'?'+st:''));
  if(!sel.length&&!f.m&&!f.t&&!f.y&&!f.c){out.innerHTML='<p class="note">'+esc(U.start)+'</p>';close.innerHTML='';$('cnt').textContent='';return}
  var base=D.d.filter(okF), full=base.filter(function(d){return sel.every(function(k){return has(d,k)})});
  $('cnt').textContent=full.length;
  var lim=60;out.innerHTML=full.length?'<div class="related">'+full.slice(0,lim).map(function(d){return card(d)}).join('')+'</div>'+(full.length>lim?'<button type="button" class="pc more" id="more">'+esc(U.more)+' ('+(full.length-lim)+')</button>':''):'<p class="note">'+esc(U.none)+'</p>';
  var mb=$('more');if(mb)mb.onclick=function(){out.querySelector('.related').innerHTML=full.map(function(d){return card(d)}).join('');mb.remove()};
  var cl=[];
  if(sel.length&&full.length<12){
    var seen={};full.forEach(function(d){seen[d.u]=1});
    sel.forEach(function(a){
      var rest=sel.filter(function(x){return x!==a});
      swapOf(a).forEach(function(b){base.forEach(function(d){if(!seen[d.u]&&has(d,b)&&rest.every(function(k){return has(d,k)})){seen[d.u]=1;cl.push([d,U.swap.replace('{a}',nm(a)).replace('{b}',nm(b))])}})});
    });
    if(sel.length>1)sel.forEach(function(a){var rest=sel.filter(function(x){return x!==a});base.forEach(function(d){if(!seen[d.u]&&rest.every(function(k){return has(d,k)})){seen[d.u]=1;cl.push([d,U.missing.replace('{a}',nm(a))])}})});
  }
  close.innerHTML=cl.length?'<h2>'+esc(U.close)+'</h2><div class="related">'+cl.slice(0,24).map(function(x){return card(x[0],x[1])}).join('')+'</div>':'';
}
function add(k){if(k&&sel.indexOf(k)<0)sel.push(k);inp.value='';sug.innerHTML='';render()}
box.onclick=function(e){var b=e.target.closest('button');if(b){sel=sel.filter(function(x){return x!==b.dataset.k});render()}};
$('pop').onclick=function(e){var b=e.target.closest('button');if(b)add(b.dataset.k)};
inp.oninput=function(){var v=norm(inp.value.trim());if(!v){sug.innerHTML='';return}
  var r=Object.keys(D.g).filter(function(k){var g=D.g[k];return norm(g.n[L]||'').indexOf(v)>=0||norm(g.n.en||'').indexOf(v)>=0||k.indexOf(v.replace(/ /g,'_'))>=0}).sort(function(a,b){var sc=function(k){var n=norm(D.g[k].n[L]||D.g[k].n.en||k);return (n===v?0:n.indexOf(v)===0&&k.indexOf('_')<0?1:n.indexOf(v)===0?2:3)};return sc(a)-sc(b)||D.g[b].c-D.g[a].c}).slice(0,10);
  sug.innerHTML=r.map(function(k){return '<button type="button" class="pc" data-k="'+k+'">'+esc(nm(k))+' <small>'+D.g[k].c+'</small></button>'}).join('')};
sug.onclick=function(e){var b=e.target.closest('button');if(b)add(b.dataset.k)};
inp.onkeydown=function(e){if(e.key==='Enter'){e.preventDefault();var b=sug.querySelector('button');if(b)add(b.dataset.k)}};
['m','t','y','c'].forEach(function(x){$('f'+x).onchange=function(){f[x]=this.value;render()}});
$('reset').onclick=function(){sel=[];f={m:'',t:'',y:'',c:''};['m','t','y','c'].forEach(function(x){$('f'+x).value=''});render()};
fetch('/dishes/cook.json').then(function(r){return r.json()}).then(function(j){D=j;
  var q=new URLSearchParams(location.search);sel=(q.get('p')||'').split(',').filter(function(k){return D.g[k]});
  ['m','t','y','c'].forEach(function(x){var v=q.get(x)||'';f[x]=v;$('f'+x).value=v});
  var cs={};D.d.forEach(function(d){if(d.c)cs[d.c]=(cs[d.c]||0)+1});
  var opts=Object.keys(cs).sort(function(a,b){return cs[b]-cs[a]});
  $('fc').insertAdjacentHTML('beforeend','<option value="__med">'+esc(U.med)+'</option>'+opts.map(function(c){return '<option value="'+esc(c)+'">'+esc((U.cn&&U.cn[c])||c)+' ('+cs[c]+')</option>'}).join(''));
  $('fc').value=f.c;render()});
})();
"""

CSS = (".cook .pick{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}"
       ".cook .pc{font:inherit;cursor:pointer;padding:7px 12px;border-radius:999px;border:1px solid var(--line);background:var(--card);font-size:14px;font-weight:600;color:inherit}"
       ".cook .pc.on{background:var(--teal-soft);color:var(--teal);border-color:transparent}.cook .pc small{color:var(--muted)}"
       ".cook .pc.more{margin-top:14px}.cook .intro+h2{margin-top:22px}"
       ".cook .filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin:18px 0}"
       ".cook label{display:block;font-size:13px;font-weight:700;color:var(--muted)}"
       ".cook select{width:100%;margin-top:4px;padding:10px;border-radius:12px;border:1px solid var(--line);background:var(--card);font:inherit;color:inherit}"
       ".cook h2 small{color:var(--muted);font-weight:600;margin-inline-start:6px}"
       ".cook .bar{display:flex;justify-content:space-between;align-items:center;gap:10px}")


def cook_page(lang, ui, langs, dish_count, ingredients, country_label, values_common, template, fill, esc, brand, path, SITE):
    T = UI[lang]
    pop = sorted(ingredients, key=lambda k: -ingredients[k]['c'])
    pop = [k for k in pop if k not in ('onion', 'garlic', 'lemon', 'butter', 'olive_oil', 'parsley', 'cumin', 'cinnamon',
                                       'cardamom', 'saffron', 'cilantro', 'ginger', 'chili', 'scallion', 'lime', 'milk',
                                       'cream', 'soy_sauce', 'water', 'oil', 'salt')][:18]
    pname = lambda k: ingredients[k]['n'].get(lang) or ingredients[k]['n'].get('en') or k.replace('_', ' ')
    sel = lambda fid, label, opts: (f'<div><label for="f{fid}">{esc(label)}</label><select id="f{fid}"><option value="">{esc(T["any"])}</option>'
                                    + ''.join(f'<option value="{k}">{esc(v)}</option>' for k, v in opts) + '</select></div>')
    main = (f'<div class="cook"><h1>{esc(T["h1"])}</h1><p class="intro">{esc(T["intro"])}</p>'
            f'<h2>{esc(T["products"])}</h2><input class="search" id="prod" type="search" autocomplete="off" placeholder="{esc(T["products_ph"])}" aria-label="{esc(T["products"])}">'
            f'<div class="pick" id="sug"></div><div class="pick" id="chips"></div>'
            f'<p class="note">{esc(T["popular"])}:</p><div class="pick" id="pop">'
            + ''.join(f'<button type="button" class="pc" data-k="{k}">{esc(pname(k))}</button>' for k in pop) + '</div>'
            f'<div class="filters">{sel("m", T["method"], T["m"].items())}{sel("t", T["taste"], T["t"].items())}'
            f'{sel("y", T["type"], [(k, T["y"][k]) for k in ["main", "soup", "salad", "snack", "breakfast", "side", "bread", "dessert", "drink"]])}'
            f'{sel("c", T["cuisine"], [])}</div>'
            f'<div class="bar"><h2>{esc(T["found"])}<small id="cnt"></small></h2><button type="button" class="pc" id="reset">{esc(T["reset"])}</button></div>'
            f'<div id="res"><noscript>{esc(T["start"])}</noscript></div><div id="close"></div></div>')
    js_ui = {k: T[k] for k in ('kcal', 'none', 'close', 'swap', 'missing', 'more', 'start', 'med')}
    js_ui['cn'] = country_label(lang)
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, "cook")}" />' for l in langs)
    v = dict(values_common)
    v.update({'title': esc(T['title']), 'description': esc(T['meta'].format(n=dish_count)), 'url': SITE + path(lang, 'cook'),
              'hreflang': hreflang, 'main': main,
              'script': ('<style>' + CSS + '</style><script type="application/json" id="cook-ui">'
                         + json.dumps(js_ui, ensure_ascii=False).replace('</', '<\\/') + '</script><script>' + COOK_JS + '</script>')})
    return fill(template, v)
