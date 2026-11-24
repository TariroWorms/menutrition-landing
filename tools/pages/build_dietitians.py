#!/usr/bin/env python3
"""/for-dietitians/ (en) and /es/for-dietitians/ (es): what the app gives a dietitian, how a client shares
the PDF diary, a sign-in box (accounts are not open yet: nothing is sent) and an application form that
posts to a Google Form (field ids in dietitians_form.json).
    python3 tools/pages/build_dietitians.py
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent / 'calculators'))
sys.path.insert(0, str(HERE.parent / 'dishes'))
sys.path.insert(0, str(HERE.parent))
import build_calculators as bc  # noqa: E402
from build_dishes import SITE, esc  # noqa: E402

FORM = json.loads((HERE / 'dietitians_form.json').read_text(encoding='utf-8'))

T = json.loads((HERE / 'dietitians.json').read_text(encoding='utf-8'))

CSS = '''<style>
.dt .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:12px 0}
.dt .card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px}
.dt .card b{display:block;margin:6px 0 4px}.dt .card .e{font-size:26px}
.dt ol.flow{counter-reset:s;list-style:none;padding:0;margin:12px 0}
.dt ol.flow li{counter-increment:s;position:relative;padding:10px 0 10px 46px}
.dt ol.flow li::before{content:counter(s);position:absolute;inset-inline-start:0;top:8px;width:32px;height:32px;border-radius:50%;background:var(--teal-soft);color:var(--teal);font-weight:800;display:grid;place-items:center}
[dir=rtl] .dt ol.flow li{padding:10px 46px 10px 0}
.dt .box{background:#fff;border:1px solid var(--line);border-radius:18px;padding:18px;max-width:560px}
.dt label{display:block;font-weight:600;margin:10px 0 4px}
.dt input,.dt select,.dt textarea{width:100%;box-sizing:border-box;font:inherit;padding:11px 12px;border-radius:12px;border:1px solid rgba(39,35,32,.2);background:#fff}
.dt .chk{display:flex;gap:8px;align-items:flex-start;font-weight:400}.dt .chk input{width:auto;margin-top:4px}
.dt .btn{display:inline-block;width:100%;height:50px;border:0;border-radius:999px;background:#1d1b19;color:#fff;font:inherit;font-weight:800;font-size:16px;cursor:pointer;margin-top:14px;text-align:center;line-height:50px;text-decoration:none}
.dt .cta{width:auto;padding:0 26px}
.dt .msg{margin-top:12px;padding:12px;border-radius:12px;background:var(--teal-soft);color:var(--teal);font-weight:600}
.dt .msg[hidden]{display:none}.dt .hp{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);opacity:0;pointer-events:none}
</style>'''


def page(lang):
    t = T[lang]
    pre = '' if lang == 'en' else f'/{lang}'
    path = f'{pre}/for-dietitians/'
    C = json.loads((bc.HERE / 'calculators.json').read_text(encoding='utf-8'))
    style = re.search(r'<style>.*?</style>', (bc.HERE.parent / 'dishes' / 'template.html').read_text(encoding='utf-8'), re.S).group(0)
    tpl = (bc.HERE / 'template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    langs = [l for l in C['_ui'] if all(l in C[s] for s in C['_order'])]
    html = bc.page(lang, C['_order'][0], C, langs, tpl)
    f = t['f']
    li = lambda xs: ''.join(f'<li>{esc(x)}</li>' for x in xs)
    cards = ''.join(f'<div class="card"><span class="e">{e}</span><b>{esc(h)}</b>{esc(p)}</div>' for e, h, p in t['how'])
    opts = ''.join(f'<option>{esc(o)}</option>' for o in t['clients_opts'])
    faq = ''.join(f'<details class="card" style="margin:8px 0"><summary><b style="display:inline">{esc(q)}</b></summary><p>{esc(a)}</p></details>' for q, a in t['faq'])
    main = f'''<main class="wrap dt"><nav class="crumbs"><a href="{pre}/">{esc(t['home'])}</a> › {esc(t['h1'])}</nav>
<h1><span class="gh">🩺</span>{esc(t['h1'])}</h1>
<p class="intro">{esc(t['intro'])}</p>
<p><a class="btn cta" href="#apply">{esc(t['cta'])}</a></p>
<section class="fsec"><h2>{esc(t['pain_h'])}</h2><ul class="mlist">{li(t['pain'])}</ul></section>
<section class="fsec"><h2>{esc(t['how_h'])}</h2><div class="grid">{cards}</div></section>
<section class="fsec"><h2>{esc(t['flow_h'])}</h2><ol class="flow">{li(t['flow'])}</ol></section>
<section class="fsec"><h2>{esc(t['pdf_h'])}</h2><ul class="mlist">{li(t['pdf'])}</ul></section>
<section class="fsec"><h2>{esc(t['gain_h'])}</h2><ul class="mlist">{li(t['gain'])}</ul></section>
<section class="fsec"><h2>{esc(t['privacy_h'])}</h2><p>{esc(t['privacy'])}</p></section>
<section class="fsec" id="signin"><h2>{esc(t['login_h'])}</h2><div class="box">
<form id="dtlogin" autocomplete="off" novalidate>
<label for="dl1">{esc(t['email'])}</label><input id="dl1" type="email" autocomplete="off">
<label for="dl2">{esc(t['password'])}</label><input id="dl2" type="password" autocomplete="new-password">
<button class="btn" type="submit">{esc(t['signin'])}</button>
<p class="msg" id="dlmsg" hidden>{esc(t['login_msg'])}</p>
</form>
<p style="margin-top:12px">{esc(t['no_acc'])} <a href="#apply">{esc(t['apply_link'])}</a></p></div></section>
<section class="fsec" id="apply"><h2>{esc(t['form_h'])}</h2><p>{esc(t['form_p'])}</p><div class="box">
<form id="dtform" novalidate>
<label for="d1">{esc(f['first'])}</label><input id="d1" name="first" required autocomplete="given-name">
<label for="d2">{esc(f['last'])}</label><input id="d2" name="last" required autocomplete="family-name">
<label for="d3">{esc(f['mail'])}</label><input id="d3" name="mail" type="email" required autocomplete="email">
<label for="d4">{esc(f['country'])}</label><input id="d4" name="country" required autocomplete="country-name">
<label for="d5">{esc(f['spec'])}</label><input id="d5" name="spec">
<label for="d6">{esc(f['clients'])}</label><select id="d6" name="clients">{opts}</select>
<label for="d7">{esc(f['now'])}</label><input id="d7" name="now">
<label for="d8">{esc(f['note'])}</label><textarea id="d8" name="note" rows="3"></textarea>
<input class="hp" name="website" tabindex="-1" autocomplete="off" aria-hidden="true">
<label class="chk"><input type="checkbox" id="d9" required> {esc(t['consent'])}</label>
<button class="btn" type="submit">{esc(t['send'])}</button>
<p class="msg" id="dfmsg" hidden></p>
</form></div></section>
<section class="fsec"><h2>{esc(t['faq_h'])}</h2>{faq}</section>
</main>'''
    js = '''<script>
(function(){
var F=%s,L=%s,lang=%s;
var lg=document.getElementById("dtlogin");lg.onsubmit=function(e){e.preventDefault();document.getElementById("dl2").value="";document.getElementById("dlmsg").hidden=false};
var f=document.getElementById("dtform"),m=document.getElementById("dfmsg");
f.onsubmit=function(e){e.preventDefault();
 if(f.website.value)return;
 var req=[f.first,f.last,f.mail,f.country,document.getElementById("d9")],ok=true;
 req.forEach(function(x){var bad=x.type==="checkbox"?!x.checked:!x.value.trim()||(x.type==="email"&&!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(x.value));x.style.borderColor=bad?"#c0392b":"";if(bad)ok=false});
 if(!ok)return;
 var d=new URLSearchParams(),v=function(n){return f[n].value.trim().replace(/[|]/g,"/")};
 d.append(F.email,v("mail"));d.append(F.page,location.pathname);d.append(F.lang,lang);
 d.append(F.src,["dietitian",v("first"),v("last"),v("country"),v("spec"),v("clients"),v("now"),v("note")].join(" | "));
 var b=f.querySelector("button");b.disabled=true;
 fetch(F.action,{method:"POST",mode:"no-cors",body:d}).then(function(){f.querySelectorAll("label,input,select,textarea,button").forEach(function(x){if(x.id!=="dfmsg")x.style.display="none"});m.textContent=L.sent;m.hidden=false})
 .catch(function(){b.disabled=false;m.textContent=L.err;m.hidden=false});
};
})();
</script>''' % (json.dumps(FORM), json.dumps({'sent': t['sent'], 'err': t['err']}, ensure_ascii=False), json.dumps(lang))
    html = re.sub(r'<main class="wrap">.*?</main>\s*<script>.*?</script>', lambda m: CSS + main + js, html, count=1, flags=re.S)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', html, flags=re.S)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n?', '', html)
    alt = ''.join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{"" if l == "en" else "/" + l}/for-dietitians/" />\n' for l in T)
    alt += f'<link rel="alternate" hreflang="x-default" href="{SITE}/for-dietitians/" />\n'
    html = html.replace('</head>', alt + '</head>', 1)
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(t["title"])}' + ('' if 'Me Nutrition' in t['title'] else ' — Me Nutrition') + '</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc(t["desc"])}"', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{SITE + path}"', html, count=1)
    html = re.sub(r'<details class="langbox">.*?</details>', '', html, count=1, flags=re.S)
    html = re.sub(r'ct=calc-hdr-(\w+)', r'ct=dietitians-hdr-\1', html)
    html = html.replace(' class="on" aria-current="page"', '')
    return path, html


def main():
    for lang in T:
        path, html = page(lang)
        d = ROOT / path.strip('/')
        d.mkdir(parents=True, exist_ok=True)
        (d / 'index.html').write_text(html, encoding='utf-8')
        print(path, len(html) // 1024, 'KB')


if __name__ == '__main__':
    main()
