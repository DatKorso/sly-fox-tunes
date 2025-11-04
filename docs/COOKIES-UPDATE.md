# Обновление cookies для YouTube

## Проблема
YouTube периодически ротирует cookies в целях безопасности. Если вы видите ошибку:
```
ERROR: Sign in to confirm you're not a bot. Use --cookies-from-browser or --cookies
WARNING: The provided YouTube account cookies are no longer valid
```

Это означает, что ваши cookies устарели или недействительны.

## Решение 1: Использовать cookies из браузера (РЕКОМЕНДУЕТСЯ) ⭐

### Преимущества:
- ✅ Автоматически использует свежие cookies
- ✅ Не требует ручного обновления
- ✅ Работает с любым браузером
- ✅ Нет риска устаревания

### Настройка:

1. **Убедитесь, что вы залогинены в YouTube** в вашем браузере
2. **Обновите `.env` файл**:
   ```bash
   # Для Chrome
   COOKIES_FROM_BROWSER=chrome
   
   # Для Firefox
   COOKIES_FROM_BROWSER=firefox
   
   # Для других: edge, brave, safari, opera
   ```

3. **Проверьте конфигурацию**:
   ```bash
   uv run python scripts/test_ytdlp_config.py --browser chrome
   ```

4. **Перезапустите бот**:
   ```bash
   uv run python main.py
   ```

### Поддерживаемые браузеры:
- ✅ Chrome / Chromium
- ✅ Firefox
- ✅ Edge
- ✅ Brave
- ✅ Safari (macOS)
- ✅ Opera

## Решение 2: Обновить файл cookies (альтернатива)

### Для Chrome/Chromium:
1. Установите расширение [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
2. Войдите в YouTube аккаунт в браузере
3. Откройте любое видео YouTube
4. Нажмите на иконку расширения
5. Нажмите "Export" → выберите "Export As cookies.txt"
6. Замените старый файл `youtube_cookies.txt` новым

### Для Firefox:
1. Установите [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/)
2. Следуйте тем же шагам

## Решение 2: Использовать встроенную функцию yt-dlp

Можно использовать cookies напрямую из браузера без экспорта:

```bash
# Для Chrome на Linux
uv run yt-dlp --cookies-from-browser chrome "URL"

# Для Firefox на Linux
uv run yt-dlp --cookies-from-browser firefox "URL"
```

Для интеграции в бот, обновите `config/settings.py`:

```python
# Добавьте опцию
cookies_from_browser: str | None = None  # e.g., "chrome", "firefox"
```

## Решение 3: Обновить бот для использования cookies из браузера

Я могу добавить в бот автоматическое использование cookies из браузера.

## Важно

⚠️ **Не коммитьте cookies файл в git!** Он содержит ваши авторизационные данные.

Добавлено в `.gitignore`:
```
youtube_cookies.txt
*.cookies.txt
```

## Проверка после обновления

```bash
uv run python scripts/test_ytdlp_config.py "https://www.youtube.com/watch?v=M_lxIiJ8ck4"
```

Если всё работает, вы увидите:
```
✓ Successfully extracted video info!
```
