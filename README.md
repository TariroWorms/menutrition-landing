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
Технологии: чистый HTML + Tailwind CSS (через CDN) + немного JS. **Сборки нет.**

**Посмотреть локально перед заливкой:** просто двойной клик по `index.html` —
откроется в браузере (работает офлайн, всё вшито).

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
  фон cream `#F2EFE8` (заданы в `tailwind.config` вверху файла).
- **Новая страница** (например, /terms) — создай папку `terms/` с файлом
  `terms/index.html`, запушь → откроется на `menutrition.app/terms`.
- **Заменить картинку** — картинки вшиты base64. Чтобы поменять фото/иконку:
  положи новый файл рядом, и в HTML замени `src="data:image/...base64,...."`
  на `src="имя-файла.jpg"` (и закоммить сам файл). Либо попроси меня перевшить.

## Не трогать
- Не переименовывай `index.html` — DigitalOcean отдаёт его как корень сайта.
- Не удаляй `privacy/index.html` — на него ссылается приложение (Privacy Policy в App Store).
