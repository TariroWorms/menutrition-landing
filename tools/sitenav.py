"""Site-wide section menu under the header (all generated pages). A section that has no page in
this language links to its English version."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
D5 = {'en', 'ru', 'ar', 'it', 'el'}
FOODS = D5 | {'es', 'de'}
CALC = {'en'} | {p.parent.name for p in ROOT.glob('*/calculators/index.html')}
LABELS = {  # dishes, cook, foods, diets, allergies, calculators, weight-loss plan, app
    'en': ['Dishes', 'What to cook', 'Foods', 'Diets', 'Allergies', 'Calculators', 'Weight-loss plan', 'App'],
    'ru': ['Блюда', 'Что приготовить', 'Продукты', 'Диеты', 'Аллергии', 'Калькуляторы', 'План похудения', 'Приложение'],
    'ar': ['الأطباق', 'ماذا أطبخ', 'الأطعمة', 'الحميات', 'الحساسية', 'الحاسبات', 'خطة إنقاص الوزن', 'التطبيق'],
    'it': ['Piatti', 'Cosa cucinare', 'Alimenti', 'Diete', 'Allergie', 'Calcolatori', 'Piano dimagrante', 'App'],
    'el': ['Πιάτα', 'Τι να μαγειρέψω', 'Τρόφιμα', 'Δίαιτες', 'Αλλεργίες', 'Υπολογιστές', 'Πλάνο απώλειας βάρους', 'Εφαρμογή'],
    'es': ['Platos', 'Qué cocinar', 'Alimentos', 'Dietas', 'Alergias', 'Calculadoras', 'Plan para adelgazar', 'App'],
    'de': ['Gerichte', 'Was kochen', 'Lebensmittel', 'Diäten', 'Allergien', 'Rechner', 'Abnehmplan', 'App'],
    'fr': ['Plats', 'Que cuisiner', 'Aliments', 'Régimes', 'Allergies', 'Calculateurs', 'Plan minceur', 'Appli'],
    'pt': ['Pratos', 'O que cozinhar', 'Alimentos', 'Dietas', 'Alergias', 'Calculadoras', 'Plano de emagrecimento', 'App'],
    'nl': ['Gerechten', 'Wat koken', 'Voedingsmiddelen', 'Diëten', 'Allergieën', 'Calculators', 'Afvalplan', 'App'],
    'pl': ['Dania', 'Co ugotować', 'Produkty', 'Diety', 'Alergie', 'Kalkulatory', 'Plan odchudzania', 'Aplikacja'],
    'sv': ['Rätter', 'Vad ska jag laga', 'Livsmedel', 'Dieter', 'Allergier', 'Kalkylatorer', 'Viktminskningsplan', 'App'],
    'tr': ['Yemekler', 'Ne pişirsem', 'Besinler', 'Diyetler', 'Alerjiler', 'Hesaplayıcılar', 'Kilo verme planı', 'Uygulama'],
    'uk': ['Страви', 'Що приготувати', 'Продукти', 'Дієти', 'Алергії', 'Калькулятори', 'План схуднення', 'Застосунок'],
    'he': ['מנות', 'מה לבשל', 'מזונות', 'דיאטות', 'אלרגיות', 'מחשבונים', 'תוכנית ירידה במשקל', 'האפליקציה'],
    'hi': ['व्यंजन', 'क्या बनाएं', 'खाद्य पदार्थ', 'डाइट', 'एलर्जी', 'कैलकुलेटर', 'वज़न घटाने का प्लान', 'ऐप'],
    'id': ['Hidangan', 'Masak apa', 'Makanan', 'Diet', 'Alergi', 'Kalkulator', 'Rencana turun berat', 'Aplikasi'],
    'ja': ['料理', '何を作る？', '食品', 'ダイエット', 'アレルギー', '計算ツール', '減量プラン', 'アプリ'],
    'ko': ['요리', '뭐 만들까', '식품', '식단', '알레르기', '계산기', '다이어트 플랜', '앱'],
    'th': ['อาหาร', 'ทำอะไรกินดี', 'วัตถุดิบ', 'ไดเอท', 'ภูมิแพ้', 'เครื่องคำนวณ', 'แผนลดน้ำหนัก', 'แอป'],
    'vi': ['Món ăn', 'Nấu gì', 'Thực phẩm', 'Chế độ ăn', 'Dị ứng', 'Công cụ tính', 'Kế hoạch giảm cân', 'Ứng dụng'],
    'zh': ['菜肴', '做什么菜', '食物', '饮食法', '过敏', '计算器', '减重计划', '应用'],
}


def _pre(lang, have):
    return '/' if lang == 'en' or lang not in have else f'/{lang}/'


def sitenav(lang, here=''):
    L = LABELS.get(lang, LABELS['en'])
    links = [
        ('/app/' if lang == 'en' or lang == 'el' else f'/{lang}/app/', L[7]),
        (_pre(lang, D5) + 'dishes/', L[0]),
        (_pre(lang, D5) + 'dishes/cook/', L[1]),
        (_pre(lang, FOODS) + 'foods/', L[2]),
        (_pre(lang, D5) + 'guides/#diets', L[3]),
        (_pre(lang, D5) + 'guides/#allergies', L[4]),
        (_pre(lang, CALC) + 'calculators/', L[5]),
        (_pre(lang, CALC) + 'calculators/weight-loss-calculator/', L[6]),
    ]
    import html
    paths = [h.split('#')[0] for h, _ in links]
    best = max((p for p in paths if here.startswith(p) and p not in ('/', f'/{lang}/')), key=len, default=None)
    if best and best.endswith('/dishes/') and '/guides/' in here:
        best = None
    return '<nav class="snav" aria-label="Sections"><div class="wrap">' + ''.join(
        f'<a href="{h}"{" class=\"on\" aria-current=\"page\"" if best and h.split("#")[0] == best and "#allergies" not in h else ""}>{html.escape(t)}</a>'
        for h, t in links) + '</div></nav>' + SCROLL


CSS = ('.snav{border-bottom:1px solid var(--line);background:var(--bg,#f8f6f1)}'
       '.snav .wrap{display:flex;gap:4px;overflow-x:auto;scrollbar-width:none;padding-top:6px;padding-bottom:6px;-webkit-overflow-scrolling:touch}'
       '.snav .wrap::-webkit-scrollbar{display:none}'
       '.snav a{flex:none;padding:7px 12px;border-radius:999px;font-size:14px;font-weight:700;text-decoration:none;color:inherit;white-space:nowrap}'
       '.snav a:hover,.snav a.on{background:var(--teal-soft);color:var(--teal)}'
       '.scrb{position:fixed;right:16px;bottom:20px;z-index:60;display:flex;flex-direction:column;gap:8px;opacity:0;pointer-events:none;transition:opacity .3s}'
       '.scrb.on{opacity:1;pointer-events:auto}'
       '.scrb button{width:44px;height:44px;border-radius:50%;border:1px solid var(--line);background:rgba(255,255,255,.92);'
       'box-shadow:0 6px 18px rgba(39,35,32,.18);font:700 20px/1 system-ui,sans-serif;color:#1f1b17;cursor:pointer}'
       '[dir=rtl] .scrb{right:auto;left:16px}')


# floating "to top / to bottom" buttons: shown while the page scrolls, fade out after 2 s
SCROLL = ('<div class="scrb" id="scrb" aria-hidden="true"><button type="button" data-d="-1" aria-label="Top">↑</button>'
          '<button type="button" data-d="1" aria-label="Bottom">↓</button></div>'
          '<script>(function(){var b=document.getElementById("scrb"),t;if(!b)return;'
          'function u(){var y=scrollY,h=document.documentElement.scrollHeight-innerHeight;'
          'if(h<innerHeight*1.5){b.classList.remove("on");return}'
          'b.children[0].style.visibility=y>200?"":"hidden";b.children[1].style.visibility=y<h-200?"":"hidden";'
          'b.classList.add("on");clearTimeout(t);t=setTimeout(function(){b.classList.remove("on")},2000)}'
          'addEventListener("scroll",u,{passive:true});'
          'b.onclick=function(e){var d=e.target.dataset.d;if(d)scrollTo({top:d<0?0:document.documentElement.scrollHeight,behavior:"smooth"})}})();</script>')
