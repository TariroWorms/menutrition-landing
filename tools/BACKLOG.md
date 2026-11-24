# Backlog

## Expand the dish database (research needed)
- 2,377 dishes is not the limit: research and parse large recipe sites in the countries whose cuisines we cover.
- Priorities: Latin America and all main world cuisines first; Russian/CIS also wanted (not central).
- Fill product gaps by analogy, e.g. no buckwheat-groat dishes yet (kasha, grechka with meat) — check every
  common product has real dishes in the "What can I cook?" combinator.
- Keep the same data shape (ingredients, cooking method, texture/taste, tags, kcal/macros, i18n texts, photo).

## After any build
Run `python3 tools/site_chrome.py` after the builders: one shared footer and the «For dietitians» header button on every page (idempotent).
