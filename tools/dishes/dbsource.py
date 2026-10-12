"""Where the app's dish database comes from: the local app repo if it is on this machine,
otherwise the public copy the app itself downloads (api.menutrition.app)."""
import json
import os
import urllib.request

LOCAL = os.path.expanduser('~/Desktop/Frankly/MeNutrition/Resources/dish_database.json')
URL = 'https://api.menutrition.app/verified/dish_database.json'


def load_db(path=None):
    path = path or os.environ.get('DISH_DB') or LOCAL
    if os.path.exists(path):
        return json.load(open(path, encoding='utf-8'))
    with urllib.request.urlopen(URL, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))
