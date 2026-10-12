# Сверка базы блюд MeNutrition (dish_database.json v10, 2494 блюд)

Каждый ключ ингредиента размечен правилами (tools/dishes/ingredients.py, ветка site-langs репозитория
menutrition-landing) и сравнён с полями allergens и tags. После тире — ингредиенты, из-за которых
сработало правило. Проверка автоматическая, ложные срабатывания возможны: «chocolate» считается молочным,
готовые карри-пасты — с креветочной пастой, «broth» — бульон неизвестного происхождения.
Решение по каждому блюду за вами. Важнее всего раздел A (глютен, рыба, яйца, молоко, арахис) и B.

## A. Не отмечено: алкоголь — 1

- `tempura_shrimp` — tentsuyu_sauce

## A. Не отмечено: глютен — 7

- `cha_gio` — vermicelli
- `himmel_und_erde` — black_pudding
- `mole_negro` — tortilla
- `spring_rolls_vietnamese` — vermicelli
- `thai_spring_rolls` — vermicelli
- `tlayuda` — large_tortilla
- `yam_pla_duk_foo` — crispy_catfish

## A. Не отмечено: моллюски/ракообразные — 4

- `ayam_penyet` — sambal
- `gado_gado_jakarta` — kerupuk
- `nasi_lemak` — sambal
- `nasi_uduk` — sambal

## A. Не отмечено: молоко — 5

- `bungeoppang` — fish_shaped_waffle
- `churros_chocolate` — chocolate
- `mole_negro` — chocolate
- `mole_poblano` — chocolate
- `s_mores` — chocolate

## A. Не отмечено: орехи — 2

- `acai_bowl` — granola
- `green_smoothie_bowl` — granola

## A. Не отмечено: рыба — 1

- `kare_kare` — bagoong

## A. Не отмечено: соя — 10

- `fresh_spring_rolls` — peanut_sauce
- `kare_kare` — peanut_sauce
- `moo_satay` — peanut_sauce
- `satay` — peanut_sauce
- `satay_ayam` — peanut_sauce
- `satay_chicken` — peanut_sauce
- `satay_chicken_thai` — peanut_sauce
- `satay_pork` — peanut_sauce
- `spring_rolls_vietnamese` — peanut_sauce
- `thai_spring_rolls` — peanut_sauce

## A. Не отмечено: яйца — 9

- `atayef` — pancake
- `fish_and_chips` — batter
- `peking_duck` — pancakes
- `shrimp_wonton` — wonton_wrapper
- `shumai_pork` — wonton_wrapper
- `siu_mai` — wonton_wrapper
- `wonton_chili_oil` — wonton_wrapper
- `wonton_soup` — wonton_wrapper
- `wontons_in_chili_oil` — wonton_wrapper

## B. Тег vegetarian/vegan, но в составе животное — 6

- `açorda` (vegetarian) — broth
- `che_ba_mau` (vegan) — jelly
- `chongos_zamoranos` (vegetarian) — rennet
- `gado_gado_jakarta` (vegetarian) — kerupuk
- `halo_halo` (vegetarian) — jelly
- `jibneh_baida` (vegetarian) — rennet
