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


def mid_cta(lang, section):
    l = lang if lang in _str['mid'] else 'en'
    return (f'<aside class="midcta"><span>{html.escape(_str["mid"][l])}</span>'
            f'<a href="{link(section, "mid", lang)}" target="_blank" rel="noopener">{html.escape(_str["getapp"][l])}</a></aside>' + hub_link(lang))
