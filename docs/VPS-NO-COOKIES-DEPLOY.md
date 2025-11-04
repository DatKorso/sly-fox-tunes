# 🚀 Деплой на VPS без cookies

## Быстрый старт

### 1. Обновите код на VPS

```bash
# На VPS
cd /root/projects/sly-fox-tunes
git pull  # или загрузите обновленные файлы
```

### 2. Удалите настройку cookies из .env

```bash
# Откройте .env
nano .env

# Закомментируйте или удалите строку:
# COOKIES_FILE=youtube_cookies.txt

# Сохраните (Ctrl+O, Enter, Ctrl+X)
```

Ваш `.env` должен выглядеть так:
```bash
TELEGRAM_BOT_TOKEN=your_token_here
TEMP_DIR=temp
MAX_FILE_SIZE_MB=2000
# COOKIES_FILE=youtube_cookies.txt  ← закомментировано или удалено
LOG_LEVEL=INFO
```

### 3. Перезапустите бот

```bash
# Остановите старый процесс
pkill -9 -f "python main.py"

# Запустите обновленную версию
uv run python main.py
```

### 4. Проверьте работу

Отправьте боту проблемное видео:
```
https://www.youtube.com/watch?v=M_lxIiJ8ck4
```

Должно скачаться **без ошибок "not a bot"**! ✅

## Что изменилось в логах

### Раньше (с устаревшими cookies):
```
INFO | Using cookies file: youtube_cookies.txt
ERROR | Sign in to confirm you're not a bot
```

### Теперь (без cookies):
```
INFO | No cookies configured. Using iOS client fallback
INFO | Extracting video info from: https://...
INFO | Successfully extracted info for: Video Title
```

### Если нужен fallback:
```
WARNING | Primary method failed: ...
INFO | Trying fallback client: ios
SUCCESS | Fallback ios succeeded! Extracted: Video Title
```

## Опциональная настройка cookies

Cookies **всё ещё можно использовать** (автоматический fallback если устареют):

### Когда нужны cookies:
- Age-restricted видео (18+)
- Некоторые region-locked видео
- Приватные видео с доступом

### Как добавить:
```bash
# В .env
COOKIES_FILE=youtube_cookies.txt

# Загрузите свежий файл
scp youtube_cookies.txt root@your-vps:/root/projects/sly-fox-tunes/
```

**Преимущество**: Если cookies устареют, бот автоматически переключится на iOS fallback!

## Проверка на VPS

```bash
cd /root/projects/sly-fox-tunes

# Тест без cookies
uv run python -c "
import asyncio
from services.downloader import get_video_info

async def test():
    info = await get_video_info('https://www.youtube.com/watch?v=M_lxIiJ8ck4')
    print(f'✅ SUCCESS: {info[\"title\"]}')

asyncio.run(test())
"
```

Должно вывести:
```
✅ SUCCESS: Aviators - Sweet Dreams (Five Nights At Freddy's 4 Song)
```

## Запуск в фоне (production)

### С systemd (рекомендуется):

```bash
# Создайте service файл
sudo nano /etc/systemd/system/sly-fox-bot.service
```

Содержимое:
```ini
[Unit]
Description=Sly Fox Tunes Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/projects/sly-fox-tunes
ExecStart=/root/.local/bin/uv run python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Запуск:
```bash
sudo systemctl daemon-reload
sudo systemctl enable sly-fox-bot
sudo systemctl start sly-fox-bot

# Проверка статуса
sudo systemctl status sly-fox-bot

# Просмотр логов
sudo journalctl -u sly-fox-bot -f
```

### Со screen (простой вариант):

```bash
screen -S bot
cd /root/projects/sly-fox-tunes
uv run python main.py

# Отключиться: Ctrl+A, затем D
# Вернуться: screen -r bot
```

## Мониторинг

### Просмотр логов в реальном времени:
```bash
tail -f logs/app.log
```

### Проверка работы бота:
```bash
ps aux | grep "python main.py"
```

## Troubleshooting

### Бот не запускается
```bash
# Проверьте логи
cat logs/app.log | tail -50

# Проверьте .env
cat .env | grep -v "^#"

# Проверьте зависимости
uv sync
```

### Видео не скачиваются
```bash
# Обновите yt-dlp
uv pip install -U yt-dlp

# Проверьте тестовый скрипт
uv run python scripts/test_no_cookies.py
```

### Нужны cookies для age-restricted
```bash
# На локальной машине экспортируйте cookies
# Загрузите на VPS
scp youtube_cookies.txt root@vps:/root/projects/sly-fox-tunes/

# Добавьте в .env
echo "COOKIES_FILE=youtube_cookies.txt" >> .env

# Перезапустите
pkill -9 -f "python main.py"
uv run python main.py
```

## 🎉 Готово!

Бот теперь работает **без необходимости обновления cookies**!

Для 95%+ видео cookies больше не нужны. 
Если нужен доступ к специальному контенту - добавьте cookies опционально.
