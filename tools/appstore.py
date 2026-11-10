"""App Store link and the short «count by photo» prompt shown next to results (strings: tools/android/strings.json)."""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_cfg = json.loads((HERE / 'android' / 'config.json').read_text(encoding='utf-8'))
_str = json.loads((HERE / 'android' / 'strings.json').read_text(encoding='utf-8'))['new']
STORE, PT = _cfg['store'], _cfg['pt']
_hub = json.loads((HERE / 'features' / 'features.json').read_text(encoding='utf-8'))['calorie-counter-app']


def link(section, place, lang):
    return f'{STORE}?pt={PT}&amp;ct={section}-{place}-{lang}&amp;mt=8'


def hub_link(lang):
    """Internal link to the «calorie counter app» page in the visitor's language (empty where that page does not exist)."""
    if lang not in _hub:
        return ''
    return (f'<p class="hublink" style="margin:-8px 0 16px;font-size:14px"><a href="{"/" if lang == "en" else f"/{lang}/"}features/calorie-counter-app/">'
            f'{html.escape(_hub[lang]["name"])} →</a></p>')


_CTX = {
 "en": "Eating {name}? Log it in 3 seconds — snap a photo of your plate.",
 "ru": "{name}: запишите в дневник за 3 секунды — сфотографируйте тарелку.",
 "ar": "تناولت {name}؟ سجّله خلال 3 ثوانٍ: صوّر طبقك فقط.",
 "it": "{name}: registralo in 3 secondi — scatta una foto al piatto.",
 "el": "{name}: καταγράψτε το σε 3 δευτερόλεπτα — φωτογραφίστε το πιάτο σας.",
 "es": "{name}: regístralo en 3 segundos — haz una foto a tu plato.",
 "de": "{name}: in 3 Sekunden eintragen — fotografiere einfach deinen Teller."
}


def mid_cta(lang, section, name=None):
    """name: the dish or food on the page; its copy then speaks about that item instead of the generic line."""
    l = lang if lang in _str['mid'] else 'en'
    text = _CTX[lang].format(name=name) if name and len(name) <= 60 and lang in _CTX else _str['mid'][l]
    return (f'<aside class="midcta"><span>{html.escape(text)}</span>'
            f'<a href="{link(section, "mid", lang)}" target="_blank" rel="noopener">{html.escape(_str["getapp"][l])}</a></aside>' + hub_link(lang))
