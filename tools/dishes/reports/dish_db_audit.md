# Сверка базы блюд MeNutrition (dish_database.json v9, 2494 блюд)

Каждый ключ ингредиента размечен правилами (tools/dishes/ingredients.py, ветка site-langs репозитория
menutrition-landing) и сравнён с полями allergens и tags. После тире — ингредиенты, из-за которых
сработало правило. Проверка автоматическая, ложные срабатывания возможны: «chocolate» считается молочным,
готовые карри-пасты — с креветочной пастой, «broth» — бульон неизвестного происхождения.
Решение по каждому блюду за вами. Важнее всего раздел A (глютен, рыба, яйца, молоко, арахис) и B.

## A. Не отмечено: алкоголь — 25

- `chicken_teriyaki` — mirin
- `dragon_roll` — eel_sauce
- `kabocha_no_nimono` — mirin
- `kake_udon` — mirin
- `miso_glazed_eggplant` — mirin
- `niku_udon` — mirin
- `nikujaga` — mirin
- `oyakodon` — mirin
- `oyakodon_donburi` — mirin
- `salmon_teriyaki` — mirin
- `soba_cold` — tsuyu
- `tamagoyaki` — mirin
- `tempura_shrimp` — tentsuyu_sauce
- `tendon` — tare_sauce
- `teriyaki_chicken` — mirin
- `teriyaki_salmon` — mirin
- `unadon` — tare_sauce
- `unagi_don` — mirin
- `unagi_kabayaki` — tare_sauce
- `yaki_onigiri` — mirin
- `yakitori` — mirin
- `yakitori_kawa` — tare_sauce
- `yakitori_momo` — tare_sauce
- `yakitori_negima` — tare_sauce
- `yakitori_tsukune` — tare_sauce

## A. Не отмечено: глютен — 49

- `ayam_bakar_classic` — kecap_manis
- `bossam` — ssamjang
- `cha_gio` — vermicelli
- `char_siu_fan` — oyster_sauce
- `char_siu_pork` — hoisin
- `chiles_rellenos` — egg_batter
- `dak_galbi_cheese` — gochujang
- `doenjang_jjigae` — doenjang
- `dolsot_bibimbap` — gochujang
- `gai_pad_med_ma_muang` — oyster_sauce
- `gullac` — starch_wafer
- `himmel_und_erde` — black_pudding
- `hünkar_begendi` — bechamel
- `ikan_bakar` — kecap_manis
- `ikan_bakar_classic` — kecap_manis
- `jeyuk_bokkeum` — gochujang
- `kimchi_bokkeumbap` — gochujang
- `kimchi_jjigae` — gochujang
- `korean_bbq_beef_set` — ssamjang
- `loaded_fries_cheese` — cheese sauce
- `mapo_eggplant` — doubanjiang
- `mole_negro` — tortilla
- `nasi_goreng_classic` — kecap_manis
- `nasi_uduk` — fried_chicken
- `oden` — fishcake
- `ojingeo_bokkeum` — gochujang
- `rinderroulade` — gravy
- `samgyeopsal` — ssamjang
- `samgyeopsal_grill` — ssamjang
- `satay_ayam_classic` — kecap_manis
- `satay_kambing` — kecap_manis
- `sate_ayam` — kecap_manis
- `sate_kambing` — kecap_manis
- `shabu_shabu` — ponzu
- `soupe_de_poisson` — rouille
- `soybean_paste_stew` — doenjang
- `spring_rolls_vietnamese` — vermicelli
- `steamed_chicken_feet` — black_bean_sauce
- `tempeh_orek` — kecap_manis
- `thai_spring_rolls` — vermicelli
- `tlayuda` — large_tortilla
- `unadon` — tare_sauce
- `unagi_kabayaki` — tare_sauce
- `yakiniku_beef` — yakiniku_sauce
- `yakitori_kawa` — tare_sauce
- `yakitori_momo` — tare_sauce
- `yakitori_negima` — tare_sauce
- `yakitori_tsukune` — tare_sauce
- `yam_pla_duk_foo` — crispy_catfish

## A. Не отмечено: кунжут — 8

- `bossam` — ssamjang
- `korean_bbq_beef_set` — ssamjang
- `labneh` — za_atar
- `labneh_bil_zeit_zaatar` — za'atar
- `labneh_dip` — zaatar
- `labneh_with_olive_oil` — zaatar
- `samgyeopsal` — ssamjang
- `samgyeopsal_grill` — ssamjang

## A. Не отмечено: моллюски/ракообразные — 24

- `ayam_penyet` — sambal
- `escargots` — snails
- `escargots_bourguignonne` — snails
- `gado_gado_jakarta` — kerupuk
- `gaeng_hung_lay` — massaman_curry_paste
- `gaeng_keow_wan_tofu` — green_curry_paste
- `gaeng_pa` — jungle_curry_paste
- `green_curry` — green_curry_paste
- `green_curry_chicken` — green_curry_paste
- `khao_soi` — curry_paste
- `khao_soi_chicken` — curry_paste
- `massaman_chicken` — massaman_curry_paste
- `massaman_curry` — massaman_paste
- `nasi_lemak` — sambal
- `nasi_uduk` — sambal
- `paella_valenciana` — snails
- `panang_chicken` — panang_curry_paste
- `panang_curry` — panang_paste
- `red_curry` — red_curry_paste
- `red_curry_beef` — red_curry_paste
- `thai_fish_cake` — red_curry_paste
- `thai_fish_cakes` — red_curry_paste
- `tod_mun_pla` — red_curry_paste
- `yellow_curry` — yellow_curry_paste

## A. Не отмечено: молоко — 17

- `bungeoppang` — fish_shaped_waffle
- `churros_chocolate` — chocolate
- `churros_con_chocolate` — chocolate_sauce
- `churros_mexicanos` — chocolate_sauce
- `japanese_curry` — curry_roux
- `japanese_curry_rice` — curry_roux
- `macaron_chocolat` — egg_white, chocolate_ganache
- `mixed_grill_lebanese` — shish_tawook
- `mixed_grill_riyadh` — shish tawook, lamb tikka
- `mole_negro` — chocolate
- `mole_poblano` — chocolate
- `pisco_sour` — egg_white
- `protein_ball` — protein_powder
- `s_mores` — chocolate
- `soupe_au_pistou` — basil_pesto
- `tocino_de_cielo` — caramel
- `whiskey_sour` — egg_white

## A. Не отмечено: орехи — 3

- `acai_bowl` — granola
- `galbi_jjim` — chestnut
- `green_smoothie_bowl` — granola

## A. Не отмечено: рыба — 9

- `california_roll` — crab_stick
- `haemul_pajeon` — seafood
- `jjamppong` — seafood
- `kare_kare` — bagoong
- `pajeon` — seafood
- `soba_cold` — tsuyu
- `tempura_shrimp` — tentsuyu_sauce
- `tom_kha_seafood` — mixed_seafood
- `tom_yum_seafood` — mixed_seafood

## A. Не отмечено: соя — 11

- `fresh_spring_rolls` — peanut_sauce
- `kare_kare` — peanut_sauce
- `moo_satay` — peanut_sauce
- `satay` — peanut_sauce
- `satay_ayam` — peanut_sauce
- `satay_chicken` — peanut_sauce
- `satay_chicken_thai` — peanut_sauce
- `satay_pork` — peanut_sauce
- `spring_rolls_vietnamese` — peanut_sauce
- `tempura_shrimp` — tentsuyu_sauce
- `thai_spring_rolls` — peanut_sauce

## A. Не отмечено: яйца — 27

- `affogato` — vanilla_ice_cream
- `atayef` — pancake
- `bajadera` — nougat
- `california_roll` — crab_stick
- `chicken_nuggets_fast_food` — breading
- `chicken_wings_bbq` — ranch
- `date_milkshake` — ice cream
- `dates_milkshake` — ice cream
- `dragon_roll` — shrimp_tempura
- `falooda` — ice_cream
- `fish_and_chips` — batter
- `foie_gras_poele` — brioche
- `gnocchi_gorgonzola` — potato_gnocchi
- `gnocchi_tomato_basil` — potato_gnocchi
- `milkshake` — ice_cream
- `milkshake_vanilla` — vanilla_ice_cream
- `mochi_ice_cream` — ice_cream
- `peking_duck` — pancakes
- `pulled_pork_sandwich` — coleslaw
- `reuben_sandwich` — russian_dressing
- `schweinebraten` — potato_dumpling
- `soupe_de_poisson` — rouille
- `tempura_roll` — shrimp_tempura
- `tempura_soba` — shrimp_tempura
- `tempura_udon` — shrimp_tempura
- `tendon` — shrimp_tempura, vegetable_tempura
- `uramaki_ebi` — shrimp_tempura

## B. Тег vegetarian/vegan, но в составе животное — 13

- `açorda` (vegetarian) — broth
- `che_ba_mau` (vegan) — jelly
- `chongos_zamoranos` (vegetarian) — rennet
- `gado_gado_jakarta` (vegetarian) — kerupuk
- `gaeng_keow_wan_tofu` (vegan) — green_curry_paste
- `halo_halo` (vegetarian) — jelly
- `jibneh_baida` (vegetarian) — rennet
- `pilav` (vegetarian) — stock
- `risotto_alla_milanese` (vegetarian) — broth
- `risotto_milanese` (vegetarian) — broth
- `s_mores` (vegetarian) — marshmallow
- `soba_cold` (vegetarian) — tsuyu
- `trifle` (vegetarian) — jelly

## C. Тег vegan, но молоко/яйца/мёд — 3

- `churros_con_chocolate` — chocolate_sauce
- `churros_mexicanos` — chocolate_sauce
- `green_smoothie_bowl` — granola

## D. Ключи аллергенов вне списка — 2

- `cay` — "caffeine"
- `turk_kahvesi` — "caffeine"
