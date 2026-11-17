#!/usr/bin/env python3
"""Weight plan page (/weight-loss-plan/, /ru/weight-loss-plan/ …): like the app onboarding —
sex, age, height, weight, goal, activity, pace → daily calories, protein/fat/carbs, target date,
BMI, water and step-by-step milestones. Losing and gaining weight. Texts: tools/plan/plan_i18n.json.
Writes sitemap-plan.xml. Run after the dish build (reads the dish.css link)."""
import datetime
import html
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
sys.path.insert(0, str(ROOT / 'tools' / 'dishes'))
from sitenav import sitenav, _pre, D5, FOODS  # noqa: E402
from build_dishes import LANG_NAMES, RTL, GLOBE  # noqa: E402

SITE = 'https://menutrition.app'
HREFLANG = {'zh': 'zh-Hans'}
CITE = json.load(open(ROOT / 'tools' / 'cite.json', encoding='utf-8'))
APP = 'https://apps.apple.com/app/id6767123368?pt=128869855&ct=plan-{lang}&mt=8'
esc = html.escape


def url(lang):
    return ('/' if lang == 'en' else f'/{lang}/') + 'weight-loss-plan/'


CSS = '''<style>
.plan .form{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:20px 0;background:var(--card);border:1px solid var(--line);border-radius:22px;padding:18px}
.plan label{display:block;font-size:13px;font-weight:700;color:var(--muted)}
.plan input,.plan select{width:100%;margin-top:4px;padding:11px;border-radius:12px;border:1px solid var(--line);background:#fff;font:inherit;color:inherit}
.plan .wide{grid-column:1/-1}.plan .seg{display:flex;gap:6px;margin-top:4px}.plan .seg button{flex:1;min-width:0;padding:10px 6px;font-size:14px;line-height:1.2;border-radius:12px;border:1px solid var(--line);background:#fff;font:inherit;font-weight:700;cursor:pointer}
.plan .seg button.on{background:var(--teal);color:#fff;border-color:var(--teal)}
.plan .go{grid-column:1/-1;padding:14px;border-radius:999px;border:0;background:#1f1b17;color:#fff;font:inherit;font-weight:800;cursor:pointer}
.plan .res{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin:10px 0}
.plan .res div{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:14px}.plan .res b{display:block;font-size:24px}.plan .res span{color:var(--muted);font-size:13px}
.plan .res .big{grid-column:1/-1;background:var(--teal-soft);border-color:transparent}.plan .res .big b{font-size:40px;color:var(--teal)}
.plan table{width:100%;border-collapse:collapse;margin:10px 0;background:var(--card);border-radius:16px;overflow:hidden}
.plan td,.plan th{padding:10px 12px;border-bottom:1px solid var(--line);text-align:start}.plan th{font-size:13px;color:var(--muted)}
.plan .warn{background:#fff4e5;border-radius:14px;padding:12px 14px;margin:10px 0}
.plan ol{padding-inline-start:20px}.plan ol li{margin:6px 0}
.plan .links{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px}.plan .links a{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:14px;font-weight:700;text-decoration:none}
</style>'''

JS = r'''<script>(function(){
var T=JSON.parse(document.getElementById('plan-ui').textContent),KG=T.metric.split(/[,،、]/)[0].trim(),LB=T.imperial.split(/[,،、]/)[0].trim(),$=function(i){return document.getElementById(i)},st={sex:'f',u:'m'};
var nf=new Intl.NumberFormat(document.documentElement.lang),f1=new Intl.NumberFormat(document.documentElement.lang,{maximumFractionDigits:1});
function seg(id,key){[].forEach.call($(id).children,function(b){b.onclick=function(){st[key]=b.dataset.v;[].forEach.call($(id).children,function(x){x.classList.toggle('on',x===b)});units()}})}
seg('sx','sex');seg('un','u');
function units(){var m=st.u==='m';$('hm').hidden=!m;$('hi').hidden=m;$('wl').textContent=$('gl').textContent=m?KG:LB}
function tdee(w,h,a,s,act){return (10*w+6.25*h-5*a+(s==='m'?5:-161))*[1.2,1.375,1.55,1.725,1.9][act]}
function run(e){if(e)e.preventDefault();var m=st.u==='m',k=m?1:0.45359237;
 var w=+$('w').value*k,g=+$('g').value*k,a=+$('a').value,h=m?+$('h').value:(+$('ft').value*30.48+ +$('in').value*2.54),act=+$('act').value,p=+$('pace').value;
 if(!(w>30&&g>30&&a>=14&&h>120)){return}
 var keep=tdee(w,h,a,st.sex,act),gain=g>w,diff=Math.abs(g-w),floor=st.sex==='m'?1500:1200,out=[];
 var weekly=[0.0025,0.005,0.0075][p]*w; if(gain)weekly=[0.15,0.25,0.4][p];
 var delta=weekly*7700/7,cal=gain?keep+delta:keep-delta,low=false;
 if(!gain&&cal<floor){cal=floor;delta=keep-floor;weekly=delta*7/7700;low=true}
 var weeks=diff<0.5?0:Math.ceil(diff/Math.max(weekly,0.05)),date=new Date(Date.now()+weeks*7*864e5);
 var prot=Math.round((gain?1.8:1.6)*(gain?g:Math.min(w,g+5))),fat=Math.round(cal*0.28/9),carb=Math.max(0,Math.round((cal-prot*4-fat*9)/4));
 var bmi=function(x){return x/Math.pow(h/100,2)},disp=function(kg){return m?f1.format(kg)+' '+KG:nf.format(Math.round(kg/0.45359237))+' '+LB};
 var r='<div class="big"><span>'+T.r_cal+'</span><b>'+nf.format(Math.round(cal/10)*10)+' '+T.kcal+'</b><span>'+T.r_keep+': '+nf.format(Math.round(keep/10)*10)+' '+T.kcal+'</span></div>'
  +'<div><span>'+T.r_prot+'</span><b>'+prot+' '+T.g+'</b></div><div><span>'+T.r_fat+'</span><b>'+fat+' '+T.g+'</b></div><div><span>'+T.r_carb+'</span><b>'+carb+' '+T.g+'</b></div>'
  +(weeks?'<div><span>'+T.r_date+'</span><b>'+date.toLocaleDateString(document.documentElement.lang,{day:'numeric',month:'long',year:'numeric'})+'</b><span>'+T.r_weeks.replace('{n}',weeks)+'</span></div>':'')
  +'<div><span>'+T.r_bmi+'</span><b>'+f1.format(bmi(w))+' → '+f1.format(bmi(g))+'</b></div><div><span>'+T.r_water+'</span><b>'+f1.format(w*0.033)+' '+T.l+'</b></div>';
 $('res').innerHTML=r;var warn='';
 if(!weeks)warn+='<p class="warn">'+T.same+'</p>';if(low)warn+='<p class="warn">'+T.low+'</p>';if(bmi(g)<18.5)warn+='<p class="warn">'+T.bmi_low+'</p>';
 $('warn').innerHTML=warn;
 var rows='<tr><td>'+T.now+'</td><td>'+disp(w)+'</td><td>'+nf.format(Math.round(cal/10)*10)+'</td></tr>',cw=w,step=weeks>24?8:4;
 for(var wk=step;weeks&&wk<weeks+step;wk+=step){var n=Math.min(wk,weeks);cw=gain?Math.min(g,w+weekly*n):Math.max(g,w-weekly*n);
  var kc=tdee(cw,h,a,st.sex,act)+(n>=weeks?0:(gain?delta:-delta));if(!gain&&n<weeks)kc=Math.max(kc,floor);
  rows+='<tr><td>'+T.week.replace('{n}',n)+'</td><td>'+disp(cw)+'</td><td>'+nf.format(Math.round(kc/10)*10)+'</td></tr>';if(n>=weeks)break}
 $('steps').innerHTML=weeks?'<h2>'+T.steps_h+'</h2><table><tr><th>'+T.step_col[0]+'</th><th>'+T.step_col[1]+'</th><th>'+T.step_col[2]+'</th></tr>'+rows+'</table>':'';
 $('tips').innerHTML='<h2>'+T.tips_h+'</h2><ol>'+(gain?T.tips_gain:T.tips_lose).map(function(t){return '<li>'+t+'</li>'}).join('')+'</ol>';
 $('out').hidden=false;if(e)$('out').scrollIntoView({behavior:'smooth'});
 try{localStorage.setItem('mn-plan',JSON.stringify({st:st,v:['w','g','a','h','ft','in','act','pace'].map(function(i){return $(i).value})}))}catch(x){}}
$('pf').onsubmit=run;
try{var s=JSON.parse(localStorage.getItem('mn-plan'));if(s){['w','g','a','h','ft','in','act','pace'].forEach(function(i,j){$(i).value=s.v[j]});
 ['sx','un'].forEach(function(id,j){var key=['sex','u'][j];[].forEach.call($(id).children,function(b){if(b.dataset.v===s.st[key])b.click()})});run()}}catch(x){}
units()})();</script>'''


def build():
    T = json.load(open(HERE / 'plan_i18n.json', encoding='utf-8'))
    langs = [l for l in ['en', 'de', 'es', 'fr', 'id', 'it', 'nl', 'pl', 'pt', 'sv', 'vi', 'tr', 'uk', 'ru', 'ar', 'he', 'hi',
                         'th', 'zh', 'ja', 'ko', 'el'] if l in T and set(T[l]) >= set(T['en'])]
    style = re.search(r'<link rel="stylesheet" href="/dishes/dish\.css\?v=[^"]+" />',
                      (ROOT / 'dishes' / 'index.html').read_text(encoding='utf-8')).group(0)
    hreflang = '\n'.join(f'<link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{SITE}{url(l)}" />' for l in langs) \
        + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{url("en")}" />'
    for lang in langs:
        t = T[lang]
        d5, fd = _pre(lang, D5), _pre(lang, FOODS)
        app_page = '/app/' if lang in ('en', 'el') else f'/{lang}/app/'
        home = '/' if lang == 'en' else f'/{lang}/'
        ui = {k: t[k] for k in t if k not in ('title', 'meta', 'h1', 'lead')}
        opt = lambda items, sel: ''.join(f'<option value="{i}"{" selected" if i == sel else ""}>{esc(x)}</option>' for i, x in enumerate(items))
        jsonld = json.dumps({'@context': 'https://schema.org', '@type': 'WebApplication', 'name': t['h1'], 'url': SITE + url(lang),
                             'applicationCategory': 'HealthApplication', 'operatingSystem': 'Any', 'inLanguage': lang,
                             'description': t['meta'], 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
                             'publisher': {'@type': 'Organization', 'name': 'Me Nutrition', 'url': SITE + '/'}}, ensure_ascii=False)
        langmenu = lambda cls: (f'<details class="langbox{cls}"><summary aria-label="Language">{GLOBE}{LANG_NAMES[lang] if cls else lang.upper()}</summary><div class="lm">'
                                + ''.join(f'<a href="{url(l)}" hreflang="{l}">{LANG_NAMES[l]}</a>' for l in langs) + '</div></details>')
        page = f'''<!DOCTYPE html>
<html lang="{lang}" dir="{'rtl' if lang in RTL else 'ltr'}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<meta name="apple-itunes-app" content="app-id=6767123368, affiliate-data=pt=128869855&amp;ct=banner-plan" />
<title>{esc(t['title'])} — Me Nutrition</title>
<meta name="description" content="{esc(t['meta'])}" />
<link rel="canonical" href="{SITE}{url(lang)}" />
{hreflang}
<meta property="og:title" content="{esc(t['title'])}" /><meta property="og:description" content="{esc(t['meta'])}" />
<meta property="og:url" content="{SITE}{url(lang)}" /><meta property="og:image" content="{SITE}/og-cover.jpg" />
<link rel="icon" type="image/png" href="/appicon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" /><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500..700&family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
{style}
{CSS}
<script type="application/ld+json">{jsonld}</script>
</head>
<body>
<header><div class="wrap">
  <a class="brand" href="{home}"><img src="/appicon.png" alt="" width="32" height="32"><span class="bn"><span class="me">Me</span><span class="bn-gap"> </span><span class="nu">Nutrition</span></span></a>
  <nav class="hnav">{langmenu('')}<a class="dl" href="{APP.format(lang=lang)}" target="_blank" rel="noopener">App Store</a></nav>
</div></header>
{sitenav(lang, url(lang))}
<main class="wrap plan">
<h1>{esc(t['h1'])}</h1><p class="intro">{esc(t['lead'])}</p>
<form class="form" id="pf">
 <div><label>{esc(t['sex'])}</label><div class="seg" id="sx"><button type="button" data-v="f" class="on">{esc(t['female'])}</button><button type="button" data-v="m">{esc(t['male'])}</button></div></div>
 <div><label>{esc(t['units'])}</label><div class="seg" id="un"><button type="button" data-v="m" class="on">{esc(t['metric'])}</button><button type="button" data-v="i">{esc(t['imperial'])}</button></div></div>
 <div><label for="a">{esc(t['age'])}</label><input id="a" type="number" inputmode="numeric" min="14" max="100" value="30"></div>
 <div id="hm"><label for="h">{esc(t['height'])}, cm</label><input id="h" type="number" inputmode="decimal" min="120" max="230" value="168"></div>
 <div id="hi" hidden><label>{esc(t['height'])}, ft / in</label><div class="seg"><input id="ft" type="number" value="5" min="4" max="7"><input id="in" type="number" value="6" min="0" max="11"></div></div>
 <div><label for="w">{esc(t['weight'])}, <span id="wl">kg</span></label><input id="w" type="number" inputmode="decimal" value="80"></div>
 <div><label for="g">{esc(t['goal'])}, <span id="gl">kg</span></label><input id="g" type="number" inputmode="decimal" value="70"></div>
 <div class="wide"><label for="act">{esc(t['activity'])}</label><select id="act">{opt(t['acts'], 1)}</select></div>
 <div class="wide"><label for="pace">{esc(t['pace'])}</label><select id="pace">{opt(t['paces'], 1)}</select></div>
 <button class="go" type="submit">{esc(t['go'])}</button>
</form>
<div id="out" hidden><div class="res" id="res"></div><div id="warn"></div><div id="steps"></div><div id="tips"></div></div>
<h2>{esc(t['links_h'])}</h2>
<div class="links"><a href="{d5}dishes/cook/?y=main&amp;t=fresh">🧊 {esc(t['l_cook'])}</a><a href="{d5}guides/high-protein/">💪 {esc(t['l_prot'])}</a>
<a href="{fd}foods/">🥕 {esc(t['l_foods'])}</a><a href="{app_page}">📱 {esc(t['l_app'])}</a></div>
<p class="disclaimer">{esc(t['note'])}</p>
</main>
<footer><div class="wrap">
  <a href="{home}">Me Nutrition</a><a href="/privacy">Privacy</a><a href="/terms">Terms</a>
  {langmenu(' up')}
  <p class="cite">{esc(CITE.get(lang, CITE['en']))}</p>
</div></footer>
<script type="application/json" id="plan-ui">{json.dumps(ui, ensure_ascii=False).replace('</', '<\\/')}</script>
{JS}
<script>document.addEventListener("click",function(e){{document.querySelectorAll(".langbox").forEach(function(d){{if(d.open&&!d.contains(e.target))d.open=false}})}});</script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "dab6447bdaac4f67b7e2016c2698b9dd"}}'></script><!-- End Cloudflare Web Analytics --><script defer src="/android.js"></script>
</body>
</html>
'''
        p = ROOT / url(lang).strip('/') / 'index.html'
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(page, encoding='utf-8')
    today = datetime.date.today().isoformat()
    alts = ''.join(f'\n    <xhtml:link rel="alternate" hreflang="{HREFLANG.get(l, l)}" href="{SITE}{url(l)}"/>' for l in langs)
    (ROOT / 'sitemap-plan.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + ''.join(f'  <url>\n    <loc>{SITE}{url(l)}</loc>\n    <lastmod>{today}</lastmod>\n    <priority>0.9</priority>{alts}\n  </url>\n' for l in langs)
        + '</urlset>\n', encoding='utf-8')
    print('plan pages:', len(langs))


if __name__ == '__main__':
    build()
