#!/usr/bin/env python3
"""Calculator pages: /calculators/<slug>/ and /<lang>/calculators/<slug>/ (calories, protein, BMI).

Texts: tools/calculators/calculators.json. The maths runs in the browser (no data leaves the page).
    python3 tools/calculators/build_calculators.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / 'dishes'))
sys.path.insert(0, str(HERE.parent))
from appstore import mid_cta  # noqa: E402
from build_dishes import LANG_NAMES, RTL, SITE, brand, esc, fill, lang_menu, md  # noqa: E402

STORE = 'https://apps.apple.com/app/id6767123368'


def cpath(lang, slug=None):
    return ('/' if lang == 'en' else f'/{lang}/') + 'calculators/' + (f'{slug}/' if slug else '')


def local(lang, section):
    return f'/{lang}/{section}/' if lang != 'en' and (ROOT / lang / section / 'index.html').exists() else f'/{section}/'


def opts(items):
    return ''.join(f'<option value="{i}">{esc(x)}</option>' for i, x in enumerate(items))


def form(slug, U, T):
    units = (f'<div class="row"><div><label>&nbsp;</label><div class="seg" data-units>'
             f'<button type="button" class="on" data-u="m">{esc(U["metric"])}</button>'
             f'<button type="button" data-u="i">{esc(U["imperial"])}</button></div></div></div>')
    height = (f'<div><label>{esc(U["height"])}</label><div class="m-only"><input type="number" inputmode="decimal" name="cm" min="100" max="250" placeholder="{esc(U["cm"])}"></div>'
              f'<div class="i-only two" hidden><input type="number" inputmode="numeric" name="ft" min="3" max="8" placeholder="{esc(U["ft"])}">'
              f'<input type="number" inputmode="numeric" name="in" min="0" max="11" placeholder="{esc(U["in"])}"></div></div>')
    weight = (f'<div><label>{esc(U["weight"])}</label><input type="number" inputmode="decimal" name="w" min="25" max="350" '
              f'data-ph-m="{esc(U["kg"])}" data-ph-i="{esc(U["lb"])}" placeholder="{esc(U["kg"])}"></div>')
    sex = (f'<div><label>{esc(U["sex"])}</label><div class="seg" data-sex><button type="button" class="on" data-s="f">{esc(U["female"])}</button>'
           f'<button type="button" data-s="m">{esc(U["male"])}</button></div></div>')
    age = f'<div><label>{esc(U["age"])}</label><input type="number" inputmode="numeric" name="age" min="18" max="100" placeholder="{esc(U["years"])}"></div>'
    F = T['form']
    if slug == 'calorie-calculator':
        rows = (f'<div class="row">{sex}{age}</div><div class="row">{height}{weight}</div>'
                f'<div class="row"><div><label>{esc(U["activity"])}</label><select name="act">{opts(F["activity_levels"])}</select></div>'
                f'<div><label>{esc(F["goal"])}</label><select name="goal">{opts(F["goals"])}</select></div></div>')
    elif slug == 'protein-calculator':
        rows = f'<div class="row">{weight}<div><label>{esc(F["goal"])}</label><select name="goal">{opts(F["goals"])}</select></div></div>'
    else:
        rows = f'<div class="row">{height}{weight}</div>'
    return (f'<form class="calc" data-calc="{slug}" novalidate>{units}{rows}'
            f'<button class="go" type="submit">{esc(U["calculate"])}</button><div class="cres" aria-live="polite"></div></form>')


SCRIPT = r'''<script>
(function(){
  var f=document.querySelector('form.calc'); if(!f) return;
  var R=%s, lang=document.documentElement.lang, kind=f.dataset.calc, units='m', sex='f';
  var nf=function(x,d){return new Intl.NumberFormat(lang,{maximumFractionDigits:d||0}).format(x)};
  var v=function(n){var e=f.elements[n];return e&&e.value!==''?parseFloat(e.value):NaN};
  f.querySelectorAll('[data-units] button').forEach(function(b){b.onclick=function(){units=b.dataset.u;
    f.querySelectorAll('[data-units] button').forEach(function(x){x.classList.toggle('on',x===b)});
    f.querySelectorAll('.m-only').forEach(function(x){x.hidden=units!=='m'});f.querySelectorAll('.i-only').forEach(function(x){x.hidden=units!=='i'});
    var w=f.elements.w; if(w) w.placeholder=w.dataset[units==='m'?'phM':'phI'];}});
  f.querySelectorAll('[data-sex] button').forEach(function(b){b.onclick=function(){sex=b.dataset.s;
    f.querySelectorAll('[data-sex] button').forEach(function(x){x.classList.toggle('on',x===b)});}});
  function kg(){var w=v('w');return units==='m'?w:w*0.45359237}
  function cm(){return units==='m'?v('cm'):(v('ft')*12+(isNaN(v('in'))?0:v('in')))*2.54}
  f.onsubmit=function(e){e.preventDefault();var out=f.querySelector('.cres'),h='';
    var w=kg(),hc=cm();
    if(kind==='calorie-calculator'){var a=v('age');if(!(w>25&&hc>100&&a>=18))return;
      var bmr=10*w+6.25*hc-5*a+(sex==='m'?5:-161),act=[1.2,1.375,1.55,1.725,1.9][+f.elements.act.value],tdee=bmr*act,g=+f.elements.goal.value;
      var t=tdee+[-500,-250,0,300][g],floor=sex==='m'?1500:1200,warn='';if(g<2&&t<floor){t=floor;warn=R.floor.replace(/\{floor\}/g,nf(floor));}
      var r50=function(x){return Math.round(x/10)*10};
      h='<div>'+R.target+'</div><div class="big">'+nf(r50(t))+'<small>'+R.kcal_day+'</small></div>'+(g!==2&&!warn?'<p>'+[R.pace_lose,R.pace_slow,'',R.pace_gain][g]+'</p>':'')
       +'<p>'+R.maintain+': <b>'+nf(r50(tdee))+'</b> '+R.kcal_day+'</p><p>'+R.bmr+': <b>'+nf(r50(bmr))+'</b> '+R.kcal_day+'</p>'+(warn?'<p class="warn">'+warn+'</p>':'');}
    else if(kind==='protein-calculator'){if(!(w>25))return;var r=[[0.8,0.8],[1.0,1.2],[1.4,2.0],[1.6,2.0]][+f.elements.goal.value];
      var lo=Math.round(w*r[0]),hi=Math.round(w*r[1]),txt=lo===hi?nf(lo):nf(lo)+'–'+nf(hi);
      h='<div>'+R.target+'</div><div class="big">'+txt+'<small>'+R.g_day+'</small></div><p>'+(r[0]===r[1]?R.per_kg.replace(/\{lo\}\s*[–-]\s*\{hi\}/,'{lo}'):R.per_kg).replace('{lo}',nf(r[0],1)).replace('{hi}',nf(r[1],1))+'</p><p>'+R.per_meal.replace('{n}',nf(Math.round(hi/3.5)))+'</p>';}
    else{if(!(w>25&&hc>100))return;var m=hc/100,b=w/(m*m),c=b<18.5?0:b<25?1:b<30?2:3,lo=18.5*m*m,hi=24.9*m*m;
      if(units==='i'){lo/=0.45359237;hi/=0.45359237;}
      h='<div>'+R.target+'</div><div class="big">'+nf(b,1)+'</div><p><b>'+R.cats[c]+'</b></p><p>'+R.range.replace('{lo}',nf(lo)).replace('{hi}',nf(hi)).replace('{unit}',units==='m'?R.kg:R.lb)+'</p>';}
    out.innerHTML=h;out.classList.add('show');};
})();
</script>'''


def page(lang, slug, C, langs, template):
    U, T, meta = C['_ui'][lang], C[slug][lang], C['_meta'][slug]
    res = dict(T['result'])
    res.update({'kg': U['kg'], 'lb': U['lb']})
    res = {k: (esc(v) if isinstance(v, str) else [esc(x) for x in v]) for k, v in res.items()}
    faq = ''.join(f'<details class="faq"><summary>{esc(q)}</summary><p>{brand(esc(a))}</p></details>' for q, a in T['faq'])
    more = ''.join(f'<a href="{cpath(lang, s)}"><span class="em">{C["_meta"][s]["emoji"]}</span><div>{esc(C[s][lang]["name"])}</div></a>'
                   for s in C['_order'] if s != slug)
    ld = [{'@context': 'https://schema.org', '@type': 'FAQPage', 'inLanguage': lang,
           'mainEntity': [{'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in T['faq']]},
          {'@context': 'https://schema.org', '@type': 'WebApplication', 'name': T['name'], 'applicationCategory': 'HealthApplication',
           'operatingSystem': 'Any', 'url': SITE + cpath(lang, slug), 'inLanguage': lang,
           'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}}]
    values = {
        'lang': lang, 'dir': 'rtl' if lang in RTL else 'ltr', 'title': esc(T['title']), 'description': esc(T['meta']),
        'url': SITE + cpath(lang, slug), 'home': '/' if lang == 'en' else f'/{lang}/', 'index': cpath(lang),
        'hreflang': '\n'.join(f'<link rel="alternate" hreflang="{l}" href="{SITE + cpath(l, slug)}" />' for l in langs),
        'jsonld': '\n'.join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld),
        'emoji': meta['emoji'], 'name': esc(T['name']), 'lead': brand(md(T['lead'])), 'calc': form(slug, U, T), 'mid': mid_cta(lang, 'calc'),
        'how': ''.join(f'<p>{brand(md(x))}</p>' for x in T['how']), 'faq': faq,
        'sources': ''.join(f'<li><a href="{esc(u)}" rel="noopener" target="_blank">{esc(n)}</a></li>' for n, u in T['sources']),
        'more': f'<div class="related">{more}</div>', 'store': f'{STORE}?pt=128869855&amp;ct=calc-cta-{lang}&amp;mt=8',
        'dishes': local(lang, 'dishes'), 'guides': local(lang, 'guides'),
        'langs': ''.join(f'<a href="{cpath(l, slug)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs),
        'langmenu': lang_menu(lang, langs, lambda l: cpath(l, slug)),
        'script': SCRIPT % json.dumps(res, ensure_ascii=False),
    }
    values.update({f'u.{k}': brand(esc(v)) for k, v in U.items()})
    return fill(template, values)


def index(lang, C, langs, template):
    U = C['_ui'][lang]
    cards = ''.join(f'<a href="{cpath(lang, s)}"><span class="em">{C["_meta"][s]["emoji"]}</span><div>{esc(C[s][lang]["name"])}'
                    f'<span>{brand(esc(C[s][lang]["lead"]))}</span></div></a>' for s in C['_order'])
    html = page(lang, C['_order'][0], C, langs, template)
    # reuse the page shell: swap the body of <main> for the list of calculators
    main = (f'<main class="wrap"><nav class="crumbs"><a href="{"/" if lang == "en" else f"/{lang}/"}">{esc(U["home"])}</a> › {esc(U["calculators"])}</nav>'
            f'<h1><span class="gh">🧮</span>{esc(U["index_h"])}</h1><p class="intro">{esc(U["index_p"])}</p>'
            f'<section><div class="related fidx">{cards}</div></section><p class="note" style="margin-top:24px">{esc(U["note"])}</p></main>')
    html = re.sub(r'<main class="wrap">.*?</main>\s*<script>.*?</script>', lambda m: main, html, flags=re.S)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', html, flags=re.S)
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(U["index_title"])} — Me Nutrition</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc(U["index_meta"])}"', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{SITE + cpath(lang)}"', html, count=1)
    html = re.sub(r'(<link rel="alternate" hreflang="(\w+)" href=")[^"]*(" />)', lambda m: f'{m.group(1)}{SITE + cpath(m.group(2))}{m.group(3)}', html)
    html = re.sub(r'<details class="langbox">.*?</details>', lambda m: lang_menu(lang, langs, cpath), html, count=1, flags=re.S)
    return html


def main():
    C = json.loads((HERE / 'calculators.json').read_text(encoding='utf-8'))
    style = re.search(r'<style>.*?</style>', (HERE.parent / 'dishes' / 'template.html').read_text(encoding='utf-8'), re.S).group(0)
    tpl = (HERE / 'template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    langs = [l for l in C['_ui'] if all(l in C[s] for s in C['_order'])]
    urls = []
    for lang in langs:
        for slug in C['_order']:
            p = ROOT / cpath(lang, slug).strip('/') / 'index.html'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(page(lang, slug, C, langs, tpl), encoding='utf-8')
            urls.append(SITE + cpath(lang, slug))
        (ROOT / cpath(lang).strip('/') / 'index.html').write_text(index(lang, C, langs, tpl), encoding='utf-8')
        urls.append(SITE + cpath(lang))
    (ROOT / 'sitemap-calculators.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + ''.join(f'  <url><loc>{u}</loc></url>\n' for u in sorted(urls)) + '</urlset>\n', encoding='utf-8')
    print(f'{len(langs)} languages → {len(urls)} pages')


if __name__ == '__main__':
    main()
