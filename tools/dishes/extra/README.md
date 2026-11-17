# Extra dishes (site-side)

New dishes researched for the website, in the same format as the app's `dish_database.json`
(`db/<db_key>.json` = one entry of `dishes`, plus `db_key`). `build_dishes.py` merges them into the
app database at build time (app entries win on key clash). Texts are in `../content/<db_key>.json`
as for every other dish. New ingredient keys get names in `ingredient_names.json`.
Plan: hand the whole `db/` folder over to the app so the app and the site share the numbers.
