#!/usr/bin/env python3
"""One footer for every page and a «For dietitians» button in every header (run after the builders; idempotent).

Footer columns: brand · Dishes (all dishes, write what you ate, diets & allergies, foods, calculators, how we count)
· For you (users → the app, dietitians → sign-in) · Legal · Contact. Texts come from i18n.json (the home/app
page strings, English taken from app/index.html) and tools/pages/dietitians.json. The page's own language
switcher and citation line, if any, are kept under the columns.
    python3 tools/site_chrome.py
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
I18N = json.loads((ROOT / 'i18n.json').read_text(encoding='utf-8'))
DT = json.loads((ROOT / 'tools' / 'pages' / 'dietitians.json').read_text(encoding='utf-8'))
import sys  # noqa: E402
sys.path.insert(0, str(ROOT / 'tools'))
from sitenav import LABELS  # noqa: E402

EN = {'nav_dishes': 'Dishes', 'dg_all': 'All dishes', 'try_h': 'Write what you ate', 'foot_guides': 'Diets & allergies',
      'foot_foods': 'Foods: calories per 100 g', 'foot_calc': 'Calorie & protein calculators', 'foot_method': 'How we count',
      'foot_legal': 'Legal', 'foot_privacy': 'Privacy Policy', 'foot_terms': 'Terms of Use', 'foot_contact': 'Contact',
      'foot_store': 'App Store page'}
FOR_USERS = {'en': 'For users', 'ru': 'Пользователям', 'es': 'Para usuarios', 'de': 'Für Nutzer', 'fr': 'Utilisateurs', 'it': 'Per gli utenti',
             'pt': 'Para usuários', 'nl': 'Voor gebruikers', 'pl': 'Dla użytkowników', 'sv': 'För användare', 'tr': 'Kullanıcılar için',
             'uk': 'Користувачам', 'he': 'למשתמשים', 'ar': 'للمستخدمين', 'hi': 'उपयोगकर्ताओं के लिए', 'id': 'Untuk pengguna', 'vi': 'Cho người dùng',
             'th': 'สำหรับผู้ใช้', 'zh': '用户', 'ja': 'ユーザーの方へ', 'ko': '사용자용', 'el': 'Για χρήστες'}
GET_APP = {'en': 'Get the app', 'ru': 'Скачать приложение', 'es': 'Descargar la app', 'de': 'App laden', 'fr': 'Télécharger l’app',
           'it': 'Scarica l’app', 'pt': 'Baixar o app', 'nl': 'App downloaden', 'pl': 'Pobierz aplikację', 'sv': 'Hämta appen',
           'tr': 'Uygulamayı indir', 'uk': 'Завантажити застосунок', 'he': 'להורדת האפליקציה', 'ar': 'حمّل التطبيق', 'hi': 'ऐप डाउनलोड करें',
           'id': 'Unduh aplikasi', 'vi': 'Tải ứng dụng', 'th': 'ดาวน์โหลดแอป', 'zh': '下载应用', 'ja': 'アプリを入手', 'ko': '앱 다운로드', 'el': 'Κατεβάστε την εφαρμογή'}
CSS = ('<style id="sfcss">.sf{border-top:1px solid rgba(39,35,32,.08);background:#f3f1ec;color:#1f1b17;font-size:14px;margin-top:48px}'
       '.sf .sfw{max-width:1152px;margin:0 auto;padding:44px 20px 20px;display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:28px}'
       '.sf .sfb{display:flex;align-items:center;gap:10px;font-weight:800;font-size:17px;text-decoration:none;color:inherit}'
       '.sf .sfb img{width:32px;height:32px;border-radius:8px}.sf .sfb .me{color:#c99a3b}.sf .sfb .nu{color:#3a9a86}'
       '.sf h3{margin:0 0 12px;font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:rgba(31,27,23,.42)}'
       '.sf ul{list-style:none;margin:0;padding:0}.sf li{margin:0 0 9px}'
       '.sf a{color:rgba(31,27,23,.68);text-decoration:none}.sf a:hover{color:#2f8f7b}'
       '.sf .sfx{max-width:1152px;margin:0 auto;padding:0 20px 24px;display:flex;flex-wrap:wrap;gap:12px 20px;align-items:center;color:rgba(31,27,23,.45);font-size:13px}'
       '.sf .sfx .cite{margin:0;width:100%}.sf .sfx p{margin:0}'
       '@media(max-width:900px){.sf .sfw{grid-template-columns:repeat(2,minmax(0,1fr))}.sf .sfw>div:first-child{grid-column:1/-1}}'
       '@media(max-width:480px){.sf .sfw{grid-template-columns:1fr}}'
       '.hdt{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:999px;border:1.5px solid #2f8f7b;color:#2f8f7b !important;'
       'font-weight:700;font-size:14px;text-decoration:none;white-space:nowrap;margin-inline-end:8px;line-height:1.1}'
       '.hdt:hover{background:#2f8f7b;color:#fff !important}@media(max-width:560px){.hdt .t{display:none}.hdt{padding:7px 10px}}</style>')
LANG = re.compile(r'<html[^>]*\slang="([a-zA-Z-]+)"')
FOOT = re.compile(r'<footer\b[^>]*>.*?</footer>', re.S)
HEAD = re.compile(r'<header\b[^>]*>.*?</header>', re.S)
STORE = 'https://apps.apple.com/app/id6767123368?pt=128869855&amp;ct=foot-{lang}&amp;mt=8'


def lp(lang, path):
    """Localised path if that page exists in this language, else the English one."""
    if lang == 'en':
        return path
    base = path.split('#')[0]
    return f'/{lang}{path}' if (ROOT / lang / base.strip('/') / 'index.html').exists() else path


def footer(lang, extra):
    t = dict(EN)
    t.update({k: v for k, v in I18N.get(lang, {}).items() if k in EN})
    if lang != 'en' and 'foot_foods' in t:
        t['foot_foods'] = re.sub(r'100 (?=\S)', '100 ', t['foot_foods'])
    e = lambda s: s.replace('&', '&amp;').replace('<', '&lt;')
    d = DT.get(lang, DT['en'])
    lab = LABELS.get(lang, LABELS['en'])
    app = lp(lang, '/app/')
    cols = [
        (t['nav_dishes'], [(lp(lang, '/dishes/'), t['dg_all']), (app + '#try', t['try_h']), (lp(lang, '/guides/'), t['foot_guides']),
                           (lp(lang, '/foods/'), t['foot_foods']), (lp(lang, '/calculators/'), t['foot_calc']),
                           (lp(lang, '/dishes/how-we-count/'), t['foot_method'])]),
        ('Me Nutrition', [(app, FOR_USERS.get(lang, FOR_USERS['en'])), (STORE.format(lang=lang), GET_APP.get(lang, GET_APP['en'])),
                          (lp(lang, '/for-dietitians/') + '#signin', d['login_h']), (lp(lang, '/for-dietitians/') + '#apply', d['apply_link'])]),
        (t['foot_legal'], [('/privacy', t['foot_privacy']), ('/terms', t['foot_terms'])]),
        (t['foot_contact'], [('mailto:support@menutrition.app', 'support@menutrition.app'), (STORE.format(lang=lang), t['foot_store'])]),
    ]
    html = ['<footer class="sf"><div class="sfw"><div><a class="sfb" href="' + lp(lang, '/') + '"><img src="/appicon.png" alt="" width="32" height="32">'
            '<span class="bn"><span class="me">Me</span><span class="bn-gap"> </span><span class="nu">Nutrition</span></span></a></div>']
    for h, items in cols:
        lis = ''.join(f'<li><a href="{u}"' + (' target="_blank" rel="noopener"' if u.startswith('https://apps') else '') + f'>{e(x)}</a></li>'
                      for u, x in items)
        html.append(f'<div><h3>{e(h)}</h3><ul>{lis}</ul></div>')
    html.append(f'</div><div class="sfx">{extra}' + ('' if 'class="cite"' in extra else '<p>© 2026 Me Nutrition</p>') + '</div></footer>')
    return ''.join(html)


def header_btn(lang):
    d = DT.get(lang, DT['en'])
    return f'<a class="hdt" href="{lp(lang, "/for-dietitians/")}#signin"><span aria-hidden="true">🩺</span><span class="t">{d["h1"]}</span></a>'


def run():
    n = 0
    for f in ROOT.rglob('*.html'):
        if any(x in f.parts for x in ('tools', 'node_modules', '.git', 'photo-review', 'widgets')) or 'embed' in f.name:
            continue
        s = f.read_text(encoding='utf-8')
        if '<footer' not in s:
            continue
        m = LANG.search(s)
        lang = (m.group(1) if m else 'en').split('-')[0]
        lang = lang if lang in DT else 'en'
        fm = FOOT.search(s)
        old = fm.group(0)
        if 'class="sf"' in old:
            extra = re.sub(r'<p>© 2026 Me Nutrition</p>$', '', re.search(r'<div class="sfx">(.*?)</div></footer>', old, re.S).group(1))
        else:
            lb = re.search(r'<details class="langbox[^"]*">.*?</details>', old, re.S)
            ct = re.search(r'<p class="cite">.*?</p>', old, re.S)
            extra = (lb.group(0) if lb else '') + (ct.group(0) if ct else '')
        new = footer(lang, extra)
        s2 = s[:fm.start()] + new + s[fm.end():]
        if 'id="sfcss"' not in s2:
            s2 = s2.replace('</head>', CSS + '</head>', 1)
        hm = HEAD.search(s2)
        if hm and 'class="hdt"' not in hm.group(0):
            h = hm.group(0)
            i = h.rfind('<a', 0, h.find('apps.apple.com')) if 'apps.apple.com' in h else -1
            if i >= 0:
                h = h[:i] + header_btn(lang) + h[i:]
                s2 = s2[:hm.start()] + h + s2[hm.end():]
        if s2 != s:
            f.write_text(s2, encoding='utf-8')
            n += 1
    print(n, 'pages')


if __name__ == '__main__':
    run()
