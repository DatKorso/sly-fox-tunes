# 🚨 Быстрое решение ошибки "Sign in to confirm you're not a bot"

## Проблема
Бот не может скачать некоторые видео с YouTube, показывая ошибку:
```
ERROR: Sign in to confirm you're not a bot
WARNING: The provided YouTube account cookies are no longer valid
```

## ⚡ Быстрое решение (1 минута)

### Вариант 1: Использовать cookies из браузера (РЕКОМЕНДУЕТСЯ)

1. Убедитесь, что вы **залогинены в YouTube** в браузере (Chrome, Firefox и т.д.)

2. Добавьте в `.env` файл одну строку:
   ```bash
   COOKIES_FROM_BROWSER=chrome  # или firefox, edge, brave, safari
   ```

3. Перезапустите бот:
   ```bash
   uv run python main.py
   ```

**Готово!** Cookies будут автоматически браться из браузера.

### Вариант 2: Обновить файл cookies

1. Установите расширение браузера:
   - **Chrome**: [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - **Firefox**: [cookies.txt](https://addons.mozilla.org/firefox/addon/cookies-txt/)

2. Откройте любое видео YouTube → нажмите на иконку расширения → Export

3. Сохраните как `youtube_cookies.txt` в корне проекта

4. Обновите `.env`:
   ```bash
   COOKIES_FILE=youtube_cookies.txt
   ```

5. Перезапустите бот

## 🔍 Проверка

Протестируйте конфигурацию:
```bash
# С браузером
uv run python scripts/test_ytdlp_config.py --browser chrome

# С файлом
uv run python scripts/test_ytdlp_config.py
```

Если видите `✓ Successfully extracted video info!` — всё работает!

## 📚 Подробная документация

См. [docs/COOKIES-UPDATE.md](../docs/COOKIES-UPDATE.md)

## ❓ Почему это происходит?

YouTube периодически ротирует cookies для безопасности. Использование cookies из браузера решает эту проблему автоматически, так как браузер сам обновляет их.
