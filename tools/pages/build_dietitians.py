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

T = {
 'en': {
  'title': 'Me Nutrition for dietitians: client food diaries with photos',
  'desc': 'Your clients log meals by photo; you get a clear PDF food diary with grams, calories, protein, fat, carbs and water for every day. Apply for a dietitian account.',
  'h1': 'For dietitians', 'home': 'Home',
  'intro': 'Your clients snap their meals with Me Nutrition. Calories, protein, fat and carbs are counted for every dish, and with one tap the client sends you a clear food diary for the days you need to review.',
  'cta': 'Apply for an account',
  'pain_h': 'Why food diaries are hard to work with',
  'pain': ['Clients forget to write meals down, or fill the diary in from memory at the end of the day.',
           'Portions are guessed: “a plate of pasta”, “some nuts”.',
           'Records arrive as screenshots, voice messages and notes in different formats.',
           'You spend part of every consultation putting the picture together instead of working with it.'],
  'how_h': 'How Me Nutrition helps your clients',
  'how': [('📸', 'Photo logging', 'The client photographs a meal; every dish on the plate is recognised separately with its weight, calories, protein, fat and carbs.'),
          ('🎙️', 'Voice, text and barcode', 'When a photo is not possible, a meal can be logged by voice, by typing or by scanning a barcode.'),
          ('💧', 'Water and weight', 'Water intake and body weight are logged in the same place, weight even by photographing the scale.'),
          ('⚠️', 'Allergens and diets', 'Allergens and diet fit (vegan, gluten-free and others) are shown for every dish.')],
  'flow_h': 'How the diary gets to you',
  'flow': ['The client logs meals in Me Nutrition as usual.',
           'Before a consultation, the client taps “Send to dietitian” and chooses the period.',
           'The app creates a PDF food diary and the client sends it to you by email or messenger.',
           'You open one tidy document instead of a pile of messages.'],
  'pdf_h': 'What is in the PDF diary',
  'pdf': ['Every day on its own page, meal by meal.',
          'Each dish with its photo, weight in grams, calories, protein, fat and carbs.',
          'Daily totals for calories and macros, with progress towards the daily target.',
          'Water intake for the day.',
          'Available in the client’s app language.'],
  'gain_h': 'What you get',
  'gain': ['Accurate data with weights instead of recollections.',
           'Photos that show what was really on the plate.',
           'Less time collecting information, more time for advice.',
           'Easy to see where and when the plan goes off track.'],
  'privacy_h': 'Privacy',
  'privacy': 'The client decides what to share and when: the diary reaches you only if the client sends it. Me Nutrition does not give anyone access to a client’s data.',
  'login_h': 'Dietitian sign-in', 'email': 'Email', 'password': 'Password', 'signin': 'Sign in',
  'login_msg': 'Dietitian accounts open after your application is approved. Please apply below — no password is needed yet.',
  'no_acc': 'No account yet?', 'apply_link': 'Apply for access',
  'form_h': 'Apply for a dietitian account',
  'form_p': 'We are opening a dietitian area where you can receive and review your clients’ diaries. Leave your details and we will contact you.',
  'f': {'first': 'First name', 'last': 'Last name', 'mail': 'Email', 'country': 'Country', 'spec': 'Specialisation (e.g. clinical, sports, weight management)',
        'clients': 'How many clients do you see per month?', 'now': 'How do clients send you their food diaries now?', 'note': 'Comment (optional)'},
  'clients_opts': ['Fewer than 10', '10–30', '30–100', 'More than 100'],
  'consent': 'I agree that Me Nutrition may contact me about the dietitian area.',
  'send': 'Send application', 'sent': 'Thank you! Your application has been sent. We will contact you by email.',
  'err': 'Could not send. Please check your connection and try again.',
  'faq_h': 'Questions',
  'faq': [('Does my client need anything special?', 'Only the Me Nutrition app on iPhone. The diary is created in the app and sent like any other file.'),
          ('Do I need to install the app?', 'No. You receive a PDF that opens on any computer or phone.'),
          ('What happens after I apply?', 'We will email you when the dietitian area is ready and set up your account.')],
 },
 'es': {
  'title': 'Me Nutrition para nutricionistas: diarios de comidas con fotos',
  'desc': 'Tus pacientes registran sus comidas con una foto y tú recibes un diario en PDF con gramos, calorías, proteínas, grasas, carbohidratos y agua de cada día. Solicita tu cuenta.',
  'h1': 'Para nutricionistas', 'home': 'Inicio',
  'intro': 'Tus pacientes fotografían sus comidas con Me Nutrition. Las calorías, proteínas, grasas y carbohidratos se calculan para cada plato y, con un toque, el paciente te envía un diario claro de los días que quieres revisar.',
  'cta': 'Solicitar una cuenta',
  'pain_h': 'Por qué cuesta trabajar con diarios de comidas',
  'pain': ['Los pacientes olvidan anotar las comidas o llenan el diario de memoria al final del día.',
           'Las porciones se calculan a ojo: «un plato de pasta», «unas nueces».',
           'Los registros llegan como capturas, audios y notas en formatos distintos.',
           'Parte de cada consulta se va en reconstruir el panorama en lugar de trabajar con él.'],
  'how_h': 'Cómo ayuda Me Nutrition a tus pacientes',
  'how': [('📸', 'Registro con foto', 'El paciente fotografía la comida y cada plato se reconoce por separado, con su peso, calorías, proteínas, grasas y carbohidratos.'),
          ('🎙️', 'Voz, texto y código de barras', 'Cuando no se puede tomar una foto, la comida se registra por voz, escribiendo o escaneando el código de barras.'),
          ('💧', 'Agua y peso', 'El agua y el peso corporal se registran en el mismo lugar; el peso, incluso con una foto de la báscula.'),
          ('⚠️', 'Alérgenos y dietas', 'Cada plato muestra sus alérgenos y si encaja en una dieta (vegana, sin gluten y otras).')],
  'flow_h': 'Cómo te llega el diario',
  'flow': ['El paciente registra sus comidas en Me Nutrition como siempre.',
           'Antes de la consulta, toca «Enviar al nutricionista» y elige el periodo.',
           'La app crea un diario en PDF y el paciente te lo envía por correo o mensajería.',
           'Abres un solo documento ordenado en lugar de un montón de mensajes.'],
  'pdf_h': 'Qué incluye el diario en PDF',
  'pdf': ['Cada día en su propia página, comida por comida.',
          'Cada plato con su foto, peso en gramos, calorías, proteínas, grasas y carbohidratos.',
          'Totales diarios de calorías y macros, con el avance hacia la meta del día.',
          'El agua del día.',
          'En el idioma de la app del paciente.'],
  'gain_h': 'Qué ganas tú',
  'gain': ['Datos precisos con pesos en lugar de recuerdos.',
           'Fotos que muestran lo que realmente había en el plato.',
           'Menos tiempo reuniendo información y más tiempo para aconsejar.',
           'Se ve con facilidad dónde y cuándo se sale del plan.'],
  'privacy_h': 'Privacidad',
  'privacy': 'El paciente decide qué compartir y cuándo: el diario te llega solo si él te lo envía. Me Nutrition no da a nadie acceso a los datos del paciente.',
  'login_h': 'Acceso para nutricionistas', 'email': 'Correo electrónico', 'password': 'Contraseña', 'signin': 'Entrar',
  'login_msg': 'Las cuentas para nutricionistas se abren cuando se aprueba tu solicitud. Envíala abajo; todavía no necesitas contraseña.',
  'no_acc': '¿Aún no tienes cuenta?', 'apply_link': 'Solicitar acceso',
  'form_h': 'Solicita tu cuenta de nutricionista',
  'form_p': 'Estamos abriendo un área para nutricionistas donde podrás recibir y revisar los diarios de tus pacientes. Déjanos tus datos y te contactaremos.',
  'f': {'first': 'Nombre', 'last': 'Apellido', 'mail': 'Correo electrónico', 'country': 'País', 'spec': 'Especialidad (p. ej., clínica, deportiva, control de peso)',
        'clients': '¿Cuántos pacientes atiendes al mes?', 'now': '¿Cómo te envían hoy tus pacientes su diario de comidas?', 'note': 'Comentario (opcional)'},
  'clients_opts': ['Menos de 10', '10–30', '30–100', 'Más de 100'],
  'consent': 'Acepto que Me Nutrition me contacte sobre el área para nutricionistas.',
  'send': 'Enviar solicitud', 'sent': '¡Gracias! Tu solicitud se ha enviado. Te escribiremos por correo.',
  'err': 'No se pudo enviar. Revisa tu conexión e inténtalo de nuevo.',
  'faq_h': 'Preguntas',
  'faq': [('¿Mi paciente necesita algo especial?', 'Solo la app Me Nutrition en iPhone. El diario se crea en la app y se envía como cualquier otro archivo.'),
          ('¿Tengo que instalar la app?', 'No. Recibes un PDF que se abre en cualquier computadora o teléfono.'),
          ('¿Qué pasa después de enviar la solicitud?', 'Te escribiremos cuando el área para nutricionistas esté lista y configuraremos tu cuenta.')],
 },
}

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
.dt .msg[hidden]{display:none}.dt .hp{position:absolute;left:-9999px}
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
 var d=new URLSearchParams();Object.keys(F.fields).forEach(function(k){if(f[k])d.append(F.fields[k],f[k].value.trim())});
 if(F.fields.lang)d.append(F.fields.lang,lang);if(F.fields.page)d.append(F.fields.page,location.pathname);
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
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(t["title"])} — Me Nutrition</title>', html, count=1)
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
