# MeNutrition — лендинг (menutrition.app)

Статический сайт. Один репозиторий → автодеплой на DigitalOcean.

## Что где
- `index.html` — главная страница. **Самодостаточная**: картинки (иконка, фото меню)
  вшиты прямо в HTML как base64. Отдельные файлы для работы сайта НЕ нужны.
- `privacy/index.html` — страница Политики конфиденциальности → открывается на `/privacy`.
- `appicon.png`, `menu.jpg`, `restaurant.jpg` — исходники картинок (для будущих правок;
  на работающем сайте не используются, т.к. всё вшито в index.html).

## Как это деплоится
- Хостинг: **DigitalOcean App Platform** (Static Site, бесплатный тариф).
- Привязан к этому репозиторию, ветка **main**, **Autodeploy включён**.
- **Любой push в `main` → сайт пересобирается за ~1–2 минуты** автоматически.
- Домен: `menutrition.app` (DNS на DigitalOcean nameservers, SSL автоматический).

## Правка с другого компьютера

### 1. Один раз: поставить git и получить доступ
```bash
# macOS: git уже есть (или: brew install git gh)
# проверить:
git --version
```
Нужен доступ на запись к репозиторию `TariroWorms/menutrition-landing`
(войти под этим GitHub-аккаунтом, либо быть добавленным в collaborators).
Проще всего авторизоваться через GitHub CLI:
```bash
gh auth login        # выбрать GitHub.com → HTTPS → войти в браузере
```

### 2. Склонировать
```bash
git clone https://github.com/TariroWorms/menutrition-landing.git
cd menutrition-landing
```

### 3. Редактировать
Открой `index.html` (или `privacy/index.html`) в любом редакторе (VS Code и т.п.).
Технологии: чистый HTML + Tailwind CSS + немного JS. **При деплое сборки нет** —
DigitalOcean просто отдаёт файлы.

Стили Tailwind **предкомпилированы** и вшиты в `index.html` (блок `<style id="tw">`),
а не подгружаются с CDN в рантайме. Поэтому правка **текста, цифр и цветов в уже
использованных классах** работает сразу — просто пушь. Но если добавляешь **новый
Tailwind-класс, которого ещё нет на странице** (например `mt-10`, `text-pink-500`),
его надо один раз перекомпилировать — см. раздел [«Стили»](#стили-tailwind-предкомпилирован).

**Посмотреть локально перед заливкой:** просто двойной клик по `index.html` —
откроется в браузере (работает офлайн, всё вшито, включая стили).

### 4. Залить (= опубликовать)
```bash
git add -A
git commit -m "что изменил"
git push
```
Через 1–2 минуты изменения будут на **menutrition.app**.
Обнови страницу жёстко (Cmd+Shift+R / Ctrl+F5) — браузер кэширует.

## Частые правки
- **Текст** — просто меняй текст между тегами в `index.html`.
- **Цвета** — фирменные: teal `#358076`, gold `#CF9A3F`, графит `#272320`,
  фон cream `#F2EFE8` (заданы в `tailwind.config.js`). Менять оттенок уже
  использованного цвета можно прямо в `index.html`; смена самих токенов в
  `tailwind.config.js` требует перекомпиляции (см. [«Стили»](#стили-tailwind-предкомпилирован)).
- **Новая страница** (например, /terms) — создай папку `terms/` с файлом
  `terms/index.html`, запушь → откроется на `menutrition.app/terms`.
- **Заменить картинку** — картинки вшиты base64. Чтобы поменять фото/иконку:
  положи новый файл рядом, и в HTML замени `src="data:image/...base64,...."`
  на `src="имя-файла.jpg"` (и закоммить сам файл). Либо попроси меня перевшить.

## Стили (Tailwind предкомпилирован)

Раньше Tailwind подключался скриптом `cdn.tailwindcss.com` и компилировал CSS
**в браузере при каждой загрузке** — из-за этого страница мерцала (FOUC) и сам
Tailwind ругался «should not be used in production». Теперь CSS собран заранее и
вшит в `index.html` (блок `<style id="tw">`), а CDN убран. Загрузка стала чистой,
без вспышек, и сайт работает полностью офлайн.

**Когда нужна перекомпиляция:** только если ты добавил/изменил **Tailwind-класс,
которого ещё не было** на странице, или поменял токены в `tailwind.config.js`.
Правка текста/цифр и переключение между уже встречающимися классами — без перекомпиляции.

```bash
# Нужен Node.js (node -v). Сам Tailwind ставить не надо — npx подтянет его на лету.

# 1) Собрать свежий CSS (сканирует index.html и privacy/index.html по tailwind.config.js)
npx -y tailwindcss@3.4.17 -c tailwind.config.js \
  -i <(printf '@tailwind base;@tailwind components;@tailwind utilities;') \
  -o /tmp/tw.css --minify

# 2) Вшить его обратно в <style id="tw"> внутри index.html
python3 - <<'PY'
import re
html = open('index.html', encoding='utf-8').read()
css  = open('/tmp/tw.css', encoding='utf-8').read().strip()
html = re.sub(r'(<style id="tw">).*?(</style>)',
              lambda m: m.group(1) + css + m.group(2), html, count=1, flags=re.DOTALL)
open('index.html', 'w', encoding='utf-8').write(html)
print('CSS обновлён')
PY

# 3) git add -A && git commit -m "..." && git push
```

Проще всего — попросить меня (Claude): я перекомпилирую и вшью сам.

## Не трогать
- Не переименовывай `index.html` — DigitalOcean отдаёт его как корень сайта.
- Не удаляй блок `<style id="tw">` в `index.html` — это все стили сайта.
- Не удаляй `privacy/index.html` — на него ссылается приложение (Privacy Policy в App Store).
