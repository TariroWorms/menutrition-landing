# Страницы блюд

Каждое блюдо собирается из трёх источников в одном формате, поэтому правка шаблона
меняет сразу все страницы на всех языках.

| Что | Откуда | Кто правит |
|---|---|---|
| Калории, БЖУ на 100 г, ингредиенты, аллергены | база приложения `dish_database.json` | чат приложения (здесь не править) |
| Диеты и аллергены на странице | `diets.py` — правила по ингредиентам (`ingredients.py`) | правила, не руками |
| Название, происхождение, описание, рецепт, советы, история | `content/<ключ блюда>.json` | по одному файлу на блюдо |
| Слова интерфейса | `ui.json` | по языку |
| Вёрстка | `template.html` (страница блюда), `index_template.html` (список) | один файл на все блюда |

## Формат `content/<ключ>.json`

```json
{
  "db_key": "kabsa",                 // ключ блюда в базе приложения
  "slug": "kabsa",                   // адрес: /dishes/kabsa/, /ru/dishes/kabsa/
  "emoji": "🍗",
  "portion_g": 400,                  // типичная порция, г (для «на порцию»)
  "related": ["shawarma"],           // ключи похожих блюд
  "review": {"status": "draft", "facts_checked": false},
  "i18n": {
    "en": {
      "name": "Chicken kabsa",
      "name_inline": "…",            // необязательно: как писать название внутри фразы
      "origin": "Saudi Arabia · Arabian Peninsula",
      "intro": "…", "history": "…",
      "recipe": {"servings": 4, "time_min": 75, "ingredients": ["…"], "steps": ["…"]},
      "tips": ["…"]
    },
    "ru": { … }
  }
}
```

Язык попадает на сайт, когда он есть в `ui.json` и во всех файлах `content/`.

## Сборка

```bash
python3 tools/dishes/build_dishes.py
```

Пишет `dishes/<slug>/index.html` (английский), `<язык>/dishes/<slug>/index.html` и списки `dishes/`, `<язык>/dishes/`.
Сверка базы с правилами ингредиентов: `python3 tools/dishes/audit.py` (отчёт в `reports/`, в git не попадает).
