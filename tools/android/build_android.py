#!/usr/bin/env python3
"""Generate /android.js (Android waitlist card) from i18n.json (home strings), strings.json and config.json (Google Form fields)."""
import json
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
S = json.loads((HERE / 'strings.json').read_text(encoding='utf-8'))
cfg = json.loads((HERE / 'config.json').read_text(encoding='utf-8'))
i18n = json.loads((ROOT / 'i18n.json').read_text(encoding='utf-8'))
D = {}
for lang in S['langs']:
    if lang in i18n:
        h = i18n[lang]
        base = {'h': h['and_h'].replace('<br>', ' ').replace('<br/>', ' '), 'p': h['and_p'], 'send': h['and_cta'], 'note': h['and_note']}
    else:
        base = S[lang]
    D[lang] = {**base, **{k: S['new'][k][lang] for k in S['new']}}
js = (HERE / 'android.tpl.js').read_text(encoding='utf-8')
js = js.replace('/*DICT*/{}', json.dumps(D, ensure_ascii=False, separators=(',', ':')))
js = js.replace('/*FORM*/{}', json.dumps(cfg, separators=(',', ':')))
(ROOT / 'android.js').write_text(js, encoding='utf-8')
print('android.js', len(js), 'bytes;', len(D), 'languages;', 'form configured' if cfg.get('action') else 'form NOT configured (mailto fallback)')
