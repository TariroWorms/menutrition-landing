"""App Store link and the short «count by photo» prompt shown next to results (strings: tools/android/strings.json)."""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
_cfg = json.loads((HERE / 'android' / 'config.json').read_text(encoding='utf-8'))
_str = json.loads((HERE / 'android' / 'strings.json').read_text(encoding='utf-8'))['new']
STORE, PT = _cfg['store'], _cfg['pt']


def link(section, place, lang):
    return f'{STORE}?pt={PT}&amp;ct={section}-{place}-{lang}&amp;mt=8'


def mid_cta(lang, section):
    l = lang if lang in _str['mid'] else 'en'
    return (f'<aside class="midcta"><span>{html.escape(_str["mid"][l])}</span>'
            f'<a href="{link(section, "mid", lang)}" target="_blank" rel="noopener">{html.escape(_str["getapp"][l])}</a></aside>')
