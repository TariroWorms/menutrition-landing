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
  (q.get('q')||'').split(/[,;]+|\s+и\s+|\s+and\s+/).forEach(function(w){w=norm(w.trim());if(!w)return;
    var best=null,bs=9;Object.keys(D.g).forEach(function(k){var g=D.g[k],a=norm(g.n[L]||''),b=norm(g.n.en||''),s=(a===w||b===w)?0:((a.indexOf(w)===0||b.indexOf(w)===0)&&k.indexOf('_')<0)?1:(a.indexOf(w)===0||b.indexOf(w)===0)?2:9;
      if(s<bs||(s===bs&&best&&g.c>D.g[best].c)){bs=s;best=k}});if(best&&bs<9&&sel.indexOf(best)<0)sel.push(best)});
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
       ".cook .filters{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:22px 0}"
       ".cook label{display:block;font-size:13px;font-weight:700;color:var(--muted)}"
       ".cook select{-webkit-appearance:none;appearance:none;width:100%;height:46px;margin-top:6px;padding:0 38px 0 14px;border-radius:14px;border:1px solid var(--line);"
       "background:var(--card) url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' fill='none' stroke='%23777' stroke-width='2'%3E%3Cpath d='M1 1l5 5 5-5'/%3E%3C/svg%3E\") no-repeat right 15px center;font:inherit;font-size:15px;color:inherit;cursor:pointer}"
       "[dir=rtl] .cook select{padding:0 14px 0 38px;background-position:left 15px center}"
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
            f'<div id="res"><noscript>{esc(T["start"])}</noscript></div><div id="close"></div>'
            f'<p class="note"><a href="{path(lang, "with")}">{esc(WITH_UI[lang]["hub"])} →</a></p></div>')
    js_ui = {k: T[k] for k in ('kcal', 'none', 'close', 'swap', 'missing', 'more', 'start', 'med')}
    js_ui['cn'] = country_label(lang)
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, "cook")}" />' for l in langs)
    v = dict(values_common)
    v.update({'title': esc(T['title']), 'description': esc(T['meta'].format(n=dish_count)), 'url': SITE + path(lang, 'cook'),
              'hreflang': hreflang, 'main': main,
              'script': ('<style>' + CSS + '</style><script type="application/json" id="cook-ui">'
                         + json.dumps(js_ui, ensure_ascii=False).replace('</', '<\\/') + '</script><script>' + COOK_JS + '</script>')})
    return fill(template, v)


# ---- "Dishes with X" landing pages: /dishes/with/<product>/ (SEO for "chicken recipes", "блюда из курицы") ----
WITH_UI = {
    'en': {'title': '{x} recipes: {n} dishes with {x_l} and their calories', 'meta': '{n} dishes with {x_l} from around the world — calories per 100 g, protein and photos. Pick by cuisine, cooking method and taste.',
           'h1': 'Dishes with {x_l}', 'intro': '{n} dishes from {c} countries that use {x_l}. Tap a dish for calories, macros and a home recipe, or combine {x_l} with other products.',
           'combine': 'Combine {x_l} with other products →', 'hub': 'Dishes by product', 'hub_h1': 'Dishes by product: what to cook from what you have',
           'hub_meta': 'Find dishes by main product: chicken, rice, eggs, potatoes, beef and more — with calories and photos.', 'more_p': 'More products'},
    'ru': {'title': 'Блюда из {x_g}: рецепты с калориями ({n})', 'meta': 'Блюда с продуктом «{x}» со всего мира ({n}) — калории на 100 г, белок и фото. Подбор по кухне, способу приготовления и вкусу.',
           'h1': 'Блюда с продуктом «{x}»', 'intro': 'Блюда, где есть «{x_l}»: {n}, из стран: {c}. Откройте блюдо, чтобы увидеть калории, БЖУ и домашний рецепт, или подберите сочетание с другими продуктами.',
           'combine': 'Подобрать с другими продуктами →', 'hub': 'Блюда по продуктам', 'hub_h1': 'Блюда по продуктам: что приготовить из того, что есть',
           'hub_meta': 'Блюда по главному продукту: курица, рис, яйца, картофель, говядина и другие — с калориями и фото.', 'more_p': 'Другие продукты'},
    'it': {'title': 'Ricette con {x_l}: {n} piatti con calorie', 'meta': '{n} piatti con {x_l} da tutto il mondo — calorie per 100 g, proteine e foto. Scegli per cucina, cottura e gusto.',
           'h1': 'Piatti con {x_l}', 'intro': '{n} piatti da {c} paesi con {x_l}. Apri un piatto per calorie, macro e ricetta, oppure abbina {x_l} ad altri ingredienti.',
           'combine': 'Abbina {x_l} ad altri ingredienti →', 'hub': 'Piatti per ingrediente', 'hub_h1': 'Piatti per ingrediente: cosa cucinare con quello che hai',
           'hub_meta': 'Trova piatti per ingrediente principale: pollo, riso, uova, patate, manzo e altro — con calorie e foto.', 'more_p': 'Altri ingredienti'},
    'el': {'title': 'Συνταγές με {x_l}: {n} πιάτα με θερμίδες', 'meta': '{n} πιάτα με {x_l} απ’ όλο τον κόσμο — θερμίδες ανά 100 g, πρωτεΐνη και φωτογραφίες. Επιλογή ανά κουζίνα, μαγείρεμα και γεύση.',
           'h1': 'Πιάτα με {x_l}', 'intro': '{n} πιάτα από {c} χώρες με {x_l}. Άνοιξε ένα πιάτο για θερμίδες, μακροθρεπτικά και συνταγή ή συνδύασε με άλλα υλικά.',
           'combine': 'Συνδύασε με άλλα υλικά →', 'hub': 'Πιάτα ανά υλικό', 'hub_h1': 'Πιάτα ανά υλικό: τι να μαγειρέψω με ό,τι έχω',
           'hub_meta': 'Βρες πιάτα ανά κύριο υλικό: κοτόπουλο, ρύζι, αυγά, πατάτες, μοσχάρι και άλλα — με θερμίδες και φωτογραφίες.', 'more_p': 'Άλλα υλικά'},
    'ar': {'title': 'وصفات {x_l}: {n} طبقًا مع السعرات', 'meta': '{n} طبقًا يحتوي على {x_l} من حول العالم — السعرات لكل 100 غ والبروتين والصور. اختر حسب المطبخ وطريقة الطهي والطعم.',
           'h1': 'أطباق تحتوي على {x_l}', 'intro': '{n} طبقًا من {c} دولة تحتوي على {x_l}. افتح الطبق لمعرفة السعرات والعناصر الغذائية والوصفة، أو اجمع {x_l} مع مكونات أخرى.',
           'combine': 'اجمع مع مكونات أخرى ←', 'hub': 'الأطباق حسب المكوّن', 'hub_h1': 'الأطباق حسب المكوّن: ماذا أطبخ مما لدي',
           'hub_meta': 'ابحث عن الأطباق حسب المكوّن الرئيسي: دجاج، أرز، بيض، بطاطس، لحم بقري وغيرها — مع السعرات والصور.', 'more_p': 'مكونات أخرى'},
}
RU_GEN = {'курица': 'курицы', 'рис': 'риса', 'яйцо': 'яиц', 'яйца': 'яиц', 'картофель': 'картофеля', 'говядина': 'говядины', 'свинина': 'свинины',
          'баранина': 'баранины', 'помидор': 'помидоров', 'креветки': 'креветок', 'сыр': 'сыра', 'баклажан': 'баклажанов', 'чечевица': 'чечевицы',
          'лосось': 'лосося', 'паста': 'пасты', 'морковь': 'моркови', 'грибы': 'грибов', 'тыква': 'тыквы', 'нут': 'нута', 'фасоль': 'фасоли',
          'капуста': 'капусты', 'шпинат': 'шпината', 'кабачок': 'кабачков', 'тунец': 'тунца', 'индейка': 'индейки', 'утка': 'утки', 'треска': 'трески',
          'творог': 'творога', 'йогурт': 'йогурта', 'хлеб': 'хлеба', 'лапша': 'лапши', 'кукуруза': 'кукурузы', 'тофу': 'тофу', 'авокадо': 'авокадо',
          'яблоко': 'яблок', 'банан': 'бананов', 'шоколад': 'шоколада', 'кальмар': 'кальмаров', 'мидии': 'мидий', 'булгур': 'булгура', 'кускус': 'кускуса',
          'перец': 'перца', 'лук': 'лука', 'огурец': 'огурцов', 'свёкла': 'свёклы', 'финики': 'фиников', 'мёд': 'мёда', 'орехи': 'орехов', 'миндаль': 'миндаля'}
SKIP_WITH = BORING | {'onion', 'garlic', 'butter', 'olive_oil', 'lemon', 'parsley', 'cumin', 'chili', 'cinnamon', 'cilantro', 'ginger', 'scallion',
                      'lime', 'cardamom', 'saffron', 'milk', 'cream', 'soy_sauce', 'black_pepper', 'paprika', 'turmeric', 'bay_leaf', 'mint',
                      'dill', 'oregano', 'thyme', 'basil', 'coriander', 'sesame_oil', 'vanilla', 'nutmeg', 'cloves', 'egg_yolk', 'sesame_seeds'}


def with_pages(out, contents, cdata, langs, tpl, common_for, fill, esc, path, SITE, top=80):
    import collections
    D, G = cdata['d'], cdata['g']
    has = lambda d, k: any(i == k or ('_' + k + '_') in ('_' + i + '_') for i in d['i'])
    keys = [k for k in sorted(G, key=lambda k: -G[k]['c']) if k not in SKIP_WITH and '_' not in k][:top]
    pages = []
    for lang in [l for l in langs if l in WITH_UI]:
        W, T = WITH_UI[lang], UI[lang]
        name = lambda k: G[k]['n'].get(lang) or G[k]['n'].get('en') or k.replace('_', ' ')
        hub_links = ''.join(f'<a href="{path(lang, "with/" + k)}">{esc(name(k))}</a>' for k in keys)
        for k in keys:
            ds = [d for d in D if has(d, k)]
            if len(ds) < 3:
                continue
            x = name(k)
            fm = dict(x=x[:1].upper() + x[1:], x_l=x, x_g=RU_GEN.get(x.lower(), x), n=len(ds), c=len({d['c'] for d in ds if d['c']}))
            groups = collections.OrderedDict((y, []) for y in TYPE_ORDER)
            for d in ds:
                groups[d['y']].append(d)
            def card(d):
                dl = lang if lang in d['n'] else 'en'
                img = (f'<img class="th" src="{d["p"]}" width="56" height="56" alt="" loading="lazy">' if d['p'] else f'<span class="em">{d["e"]}</span>')
                return f'<a href="{path(dl, d["u"])}">{img}<div>{esc(d["n"][dl])}<span>{d["k"]} {esc(T["kcal"])}</span></div></a>'
            body = ''.join(f'<section><h2>{esc(T["y"][y])}<small>{len(g)}</small></h2><div class="related">'
                           + ''.join(card(d) for d in sorted(g, key=lambda d: d['k'])) + '</div></section>' for y, g in groups.items() if g)
            main = (f'<h1>{esc(W["h1"].format(**fm))}</h1><p class="intro">{esc(W["intro"].format(**fm))}</p>'
                    f'<p><a class="pc" href="{path(lang, "cook")}?p={k}">{esc(W["combine"].format(**fm))}</a></p>{body}'
                    f'<h2>{esc(W["more_p"])}</h2><nav class="countries">{hub_links}</nav>')
            v = dict(common_for(lang))
            v.update({'title': esc(W['title'].format(**fm)), 'description': esc(W['meta'].format(**fm)),
                      'url': SITE + path(lang, 'with/' + k),
                      'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, "with/" + k)}" />' for l in langs if l in WITH_UI),
                      'main': main, 'script': '<style>.pc{display:inline-block;padding:9px 14px;border-radius:999px;background:var(--teal-soft);color:var(--teal);font-weight:700;text-decoration:none}h2 small{color:var(--muted);font-weight:600;margin-inline-start:6px}</style>'})
            p = out / path(lang, 'with/' + k).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(fill(tpl, v), encoding='utf-8')
            pages.append(p)
        v = dict(common_for(lang))
        v.update({'title': esc(W['hub_h1']), 'description': esc(W['hub_meta']), 'url': SITE + path(lang, 'with'),
                  'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + path(l, "with")}" />' for l in langs if l in WITH_UI),
                  'main': f'<h1>{esc(W["hub_h1"])}</h1><p class="intro">{esc(W["hub_meta"])}</p><nav class="countries">{hub_links}</nav>', 'script': ''})
        p = out / path(lang, 'with').strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(fill(tpl, v), encoding='utf-8')
        pages.append(p)
    return pages
