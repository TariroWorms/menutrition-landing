#!/usr/bin/env python3
"""Two English-only pages for people who write about or embed Me Nutrition: /widgets/ (embeddable calculators) and /press/ (press kit).

Layout and styles are shared with the calculator pages (tools/calculators/template.html).
    python3 tools/pages/build_pages.py
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
from build_dishes import LANG_NAMES, SITE, esc  # noqa: E402

STORE = 'https://apps.apple.com/app/id6767123368'


def shell(title, desc, path, h1_emoji, h1, main_html, script=''):
    C = json.loads((bc.HERE / 'calculators.json').read_text(encoding='utf-8'))
    style = re.search(r'<style>.*?</style>', (bc.HERE.parent / 'dishes' / 'template.html').read_text(encoding='utf-8'), re.S).group(0)
    tpl = (bc.HERE / 'template.html').read_text(encoding='utf-8').replace('{{style}}', style)
    langs = [l for l in C['_ui'] if all(l in C[s] for s in C['_order'])]
    html = bc.page('en', C['_order'][0], C, langs, tpl)
    main = (f'<main class="wrap"><nav class="crumbs"><a href="/">Home</a> › {esc(h1)}</nav>'
            f'<h1><span class="gh">{h1_emoji}</span>{esc(h1)}</h1>{main_html}</main>{script}')
    html = re.sub(r'<main class="wrap">.*?</main>\s*<script>.*?</script>', lambda m: main, html, count=1, flags=re.S)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>\n?', '', html, flags=re.S)
    html = re.sub(r'<link rel="alternate" hreflang="[^"]*" href="[^"]*" />\n?', '', html)
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(title)} — Me Nutrition</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc(desc)}"', html, count=1)
    html = re.sub(r'<link rel="canonical" href="[^"]*"', f'<link rel="canonical" href="{SITE + path}"', html, count=1)
    html = re.sub(r'<details class="langbox">.*?</details>', '', html, count=1, flags=re.S)
    html = html.replace('ct=calc-hdr-en', 'ct=page-hdr-en')
    return html


WIDGET_JS = r'''<script>
(function(){
  var D=%s, order=%s, LN=%s;
  var selC=document.getElementById('wc'), selL=document.getElementById('wl'), code=document.getElementById('wcode'), prev=document.getElementById('wprev'), btn=document.getElementById('wcopy');
  order.forEach(function(s){var o=document.createElement('option');o.value=s;o.textContent=D.en[s];selC.appendChild(o)});
  Object.keys(LN).forEach(function(l){var o=document.createElement('option');o.value=l;o.textContent=LN[l];selL.appendChild(o)});
  function esc(t){return String(t).replace(/&/g,'&amp;').replace(/"/g,'&quot;').replace(/</g,'&lt;')}
  function render(){
    var l=selL.value,s=selC.value,name=(D[l]&&D[l][s])||D.en[s];
    var url='https://menutrition.app'+(l==='en'?'':'/'+l)+'/calculators/'+s+'/';
    prev.src=(l==='en'?'':'/'+l)+'/calculators/'+s+'/?embed=1';
    code.value='<iframe src="'+url+'?embed=1" width="100%%" height="520" style="border:0;max-width:640px;display:block" loading="lazy" title="'+esc(name)+'"></iframe>\n'
      +'<p><a href="'+url+'">'+esc(name)+'</a> — <a href="https://menutrition.app/">Me Nutrition</a></p>\n'
      +'<script>window.addEventListener("message",function(e){if(e.origin==="https://menutrition.app"&&e.data&&e.data.mnHeight){document.querySelectorAll(\'iframe[src^="https://menutrition.app/"]\').forEach(function(f){if(f.contentWindow===e.source)f.style.height=e.data.mnHeight+"px"})}})<\/script>';
  }
  selC.onchange=selL.onchange=render; render();
  btn.onclick=function(){code.select();try{navigator.clipboard.writeText(code.value)}catch(e){document.execCommand('copy')}btn.textContent='Copied';setTimeout(function(){btn.textContent='Copy code'},1800)};
  window.addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.mnHeight&&e.source===prev.contentWindow)prev.style.height=Math.max(380,e.data.mnHeight)+'px'});
})();
</script>'''


def widgets():
    C = json.loads((bc.HERE / 'calculators.json').read_text(encoding='utf-8'))
    langs = [l for l in C['_ui'] if all(l in C[s] for s in C['_order'])]
    order = C['_order']
    names = {l: {s: C[s][l]['name'] for s in order} for l in langs}
    ln = {l: LANG_NAMES[l] for l in langs}
    main = f'''
  <p class="intro">Free calculators for your website or blog: calories, protein, macros, BMI, ideal weight, weight-loss timeline and water intake. Pick a calculator and a language, copy the code, paste it into your page.</p>
  <section class="fsec"><div class="row" style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
    <div><label for="wc" style="display:block;font-weight:600;margin-bottom:4px">Calculator</label><select id="wc" style="width:100%"></select></div>
    <div><label for="wl" style="display:block;font-weight:600;margin-bottom:4px">Language</label><select id="wl" style="width:100%"></select></div>
  </div></section>
  <section class="fsec"><h2>Preview</h2><iframe id="wprev" title="Calculator preview" style="border:1px solid rgba(39,35,32,.12);border-radius:16px;width:100%;max-width:640px;height:520px;background:#fff"></iframe></section>
  <section class="fsec"><h2>Embed code</h2>
    <textarea id="wcode" readonly rows="9" style="width:100%;font:13px/1.45 ui-monospace,Menlo,monospace;padding:12px;border-radius:12px;border:1px solid rgba(39,35,32,.18)"></textarea>
    <p style="margin-top:10px"><button id="wcopy" type="button" class="go" style="width:auto;padding:12px 22px">Copy code</button></p>
  </section>
  <section class="fsec"><h2>Good to know</h2>
    <p><b>Free to use.</b> Please keep the link under the calculator (it is part of the code above): it tells your readers where the numbers come from.</p>
    <p><b>Private.</b> The maths runs in the visitor’s browser. Nothing a visitor types is sent to us.</p>
    <p><b>Responsive.</b> The widget resizes with the page and adapts its height to its content.</p>
    <p><b>{len(langs)} languages.</b> Each calculator is available in every language listed above, with sources and explanations on the full page that the link points to.</p>
    <p>Estimates for healthy adults, not medical advice. Questions or a custom version: <a href="mailto:support@menutrition.app">support@menutrition.app</a>.</p>
  </section>'''
    return shell('Free nutrition calculator widgets for your website',
                 'Embed free calorie, protein, macro, BMI, ideal weight, weight-loss and water calculators on your website or blog in 22 languages. Copy the code and paste it.',
                 '/widgets/', '🧩', 'Calculator widgets', main,
                 WIDGET_JS % (json.dumps(names, ensure_ascii=False), json.dumps(order), json.dumps(ln, ensure_ascii=False)))


def press():
    shots = [('Photo of a whole meal', '/shots/lunch_intl.webp'), ('Weight by photo of the scale', '/shots/scale_kg.webp'),
             ('Menu scanner', '/shots/menu_photo_a8288b8e.webp'), ('Lock screen calories', '/shots/idea_lock.webp')]
    shot_html = ''.join(f'<li><a href="{p}" target="_blank" rel="noopener">{esc(n)}</a></li>' for n, p in shots)
    main = f'''
  <p class="intro">Everything you need to write about Me Nutrition: what it is, key facts, a short description to copy, and images. For questions or an interview, write to <a href="mailto:support@menutrition.app">support@menutrition.app</a>.</p>
  <section class="fsec"><h2>About in one paragraph</h2>
    <p>Me Nutrition is an iPhone calorie counter that works from a photo. Snap a whole meal and every dish is recognised separately, each with its own calories, protein, fat and carbs. You can also log by voice, by text or with a barcode, scan a restaurant menu, and log your weight by photographing your scale. Allergens and diets are shown on every dish, and a daily target follows your goal: lose, maintain or gain weight.</p>
    <p>Alongside the app, menutrition.app offers a free nutrition guide with calories and macros for more than 2,400 dishes from 120+ countries, a database of 9,000+ foods, and free calculators in 22 languages.</p>
  </section>
  <section class="fsec"><h2>Key facts</h2><ul class="mlist">
    <li><b>Name:</b> Me Nutrition</li>
    <li><b>Platform:</b> iPhone (App Store). Android: a waiting list is open at <a href="/#android-waitlist">menutrition.app</a>.</li>
    <li><b>Price:</b> 3 days free, then a subscription that can be cancelled any time in App Store settings.</li>
    <li><b>Languages:</b> 22 (the website is available in the same languages).</li>
    <li><b>What it counts:</b> calories, protein, fat, carbs, plus vitamins, minerals, sugar and salt.</li>
    <li><b>Ways to log:</b> photo, voice, text, barcode, menu scan.</li>
    <li><b>Food data on the site:</b> USDA FoodData Central (public domain) and ANSES CIQUAL (Licence Ouverte).</li>
    <li><b>Website:</b> <a href="/">menutrition.app</a> · <b>App Store:</b> <a href="{STORE}?pt=128869855&amp;ct=press-body-en&amp;mt=8" target="_blank" rel="noopener">Me Nutrition</a></li>
  </ul></section>
  <section class="fsec"><h2>Short description (copy and paste)</h2>
    <p><i>Me Nutrition is a calorie counter for iPhone that works from a photo: snap your meal and every dish gets its own calories and macros. It also logs by voice, text or barcode, scans restaurant menus and shows allergens and diets on every dish.</i></p>
  </section>
  <section class="fsec"><h2>Images</h2><ul class="mlist">
    <li><a href="/appicon.png" target="_blank" rel="noopener">App icon</a></li>
    <li><a href="/og-cover.png" target="_blank" rel="noopener">Cover image</a></li>
    {shot_html}
  </ul><p>Free to use when writing about Me Nutrition. Please link to <a href="/">menutrition.app</a>.</p></section>
  <section class="fsec"><h2>For your readers</h2><div class="flinks">
    <a href="/calculators/">Free nutrition calculators →</a><a href="/widgets/">Embed a calculator on your site →</a><a href="/dishes/">Calories for 2,400+ dishes →</a><a href="/foods/">Calories and nutrition per 100 g →</a>
  </div></section>'''
    return shell('Press kit', 'Press kit for Me Nutrition, the photo calorie counter for iPhone: description, key facts, images and contact.',
                 '/press/', '📰', 'Press kit', main)


def main():
    for slug, html in (('widgets', widgets()), ('press', press())):
        d = ROOT / slug
        d.mkdir(exist_ok=True)
        (d / 'index.html').write_text(html, encoding='utf-8')
        print(f'/{slug}/ ({len(html) // 1024} KB)')


if __name__ == '__main__':
    main()
