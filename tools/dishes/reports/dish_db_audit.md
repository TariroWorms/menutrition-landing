# Сверка базы блюд MeNutrition (dish_database.json v11, 2494 блюд)

Каждый ключ ингредиента размечен правилами (tools/dishes/ingredients.py, ветка site-langs репозитория
menutrition-landing) и сравнён с полями allergens и tags. После тире — ингредиенты, из-за которых
сработало правило. Проверка автоматическая, ложные срабатывания возможны: «chocolate» считается молочным,
готовые карри-пасты — с креветочной пастой, «broth» — бульон неизвестного происхождения.
Решение по каждому блюду за вами. Важнее всего раздел A (глютен, рыба, яйца, молоко, арахис) и B.

## A. Не отмечено: глютен — 6

- `cha_gio` — vermicelli
- `himmel_und_erde` — black_pudding
- `mole_negro` — tortilla
- `spring_rolls_vietnamese` — vermicelli
- `thai_spring_rolls` — vermicelli
- `tlayuda` — large_tortilla

## A. Не отмечено: моллюски/ракообразные — 4

- `ayam_penyet` — sambal
- `gado_gado_jakarta` — kerupuk
- `nasi_lemak` — sambal
- `nasi_uduk` — sambal

## A. Не отмечено: молоко — 4

- `churros_chocolate` — chocolate
- `mole_negro` — chocolate
- `mole_poblano` — chocolate
- `s_mores` — chocolate

## A. Не отмечено: рыба — 1

- `kare_kare` — bagoong

## A. Не отмечено: яйца — 3

- `atayef` — pancake
- `fish_and_chips` — batter
- `peking_duck` — pancakes

## B. Тег vegetarian/vegan, но в составе животное — 6

- `açorda` (vegetarian) — broth
- `che_ba_mau` (vegan) — jelly
- `chongos_zamoranos` (vegetarian) — rennet
- `gado_gado_jakarta` (vegetarian) — kerupuk
- `halo_halo` (vegetarian) — jelly
- `jibneh_baida` (vegetarian) — rennet
