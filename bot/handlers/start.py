"""Start command handler."""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router(name="start")


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    welcome_text = (
        "👋 <b>Привет! Я Sly Fox Tunes</b>\n\n"
        "🎵 Я помогу тебе скачать видео или аудио с YouTube!\n\n"
        "<b>Как пользоваться:</b>\n"
        "1️⃣ Отправь мне ссылку на YouTube видео\n"
        "2️⃣ Выбери формат: видео или аудио\n"
        "3️⃣ Получи файл прямо в Telegram!\n\n"
        "💡 <b>Примеры ссылок:</b>\n"
        "• https://youtube.com/watch?v=dQw4w9WgXcQ\n"
        "• https://youtu.be/dQw4w9WgXcQ\n\n"
        "❓ Используй /help для получения помощи"
    )
    await message.answer(welcome_text, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    help_text = (
        "📖 <b>Справка по использованию</b>\n\n"
        "<b>Доступные команды:</b>\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n\n"
        "<b>Как скачать видео/аудио:</b>\n"
        "1. Найди видео на YouTube\n"
        "2. Скопируй ссылку на видео\n"
        "3. Отправь ссылку мне\n"
        "4. Выбери формат (видео 🎬 или аудио 🎵)\n"
        "5. Дождись скачивания\n"
        "6. Получи файл!\n\n"
        "<b>Поддерживаемые форматы ссылок:</b>\n"
        "• youtube.com/watch?v=...\n"
        "• youtu.be/...\n"
        "• m.youtube.com/watch?v=...\n\n"
        "❗ <b>Ограничения:</b>\n"
        "• Максимальный размер файла: 2 ГБ\n"
        "• Доступны только публичные видео\n\n"
        "💬 Просто отправь ссылку и начнём!"
    )
    await message.answer(help_text, parse_mode="HTML")



@router.message(Command("test_download"))
async def cmd_test_download(message: Message) -> None:
    """
    Test command to download and re-encode video WITHOUT sending to Telegram.
    
    This command:
    1. Downloads video from hardcoded URL
    2. Saves original file with '_original' suffix
    3. Re-encodes with ffmpeg (same as real flow)
    4. Saves re-encoded file with '_reencoded' suffix
    5. Does NOT send to Telegram
    6. Does NOT delete files
    
    Files will be saved in temp/{user_id}/ directory.
    """
    from pathlib import Path
    import subprocess
    from loguru import logger
    from services.downloader import DownloaderService
    from services.file_manager import FileManager
    
    # Hardcoded test URL
    TEST_URL = "https://www.youtube.com/watch?v=xwtaekgVt9Q"
    
    if not message.from_user:
        await message.answer("❌ Не удалось определить пользователя")
        return
    
    user_id = message.from_user.id
    downloader = DownloaderService()
    file_manager = FileManager()
    
    await message.answer("🧪 **Тестовая команда запущена**\n\n"
                        f"🔗 URL: {TEST_URL}\n"
                        "⏳ Скачиваю оригинальное видео...")
    
    try:
        # Step 1: Download original video
        user_temp_dir = file_manager.get_user_temp_dir(user_id)
        original_file = await downloader.download_video(TEST_URL, user_temp_dir)
        
        logger.info(f"✅ Original video downloaded: {original_file}")
        
        # Rename original to have '_original' suffix
        original_path = Path(original_file)
        original_renamed = original_path.parent / f"{original_path.stem}_original{original_path.suffix}"
        original_path.rename(original_renamed)
        
        await message.answer(f"✅ Оригинал сохранён:\n`{original_renamed}`\n\n"
                           "🔄 Перекодирую через ffmpeg...", 
                           parse_mode="Markdown")
        
        # Step 2: Re-encode with ffmpeg (simulate Telegram preparation)
        reencoded_path = original_path.parent / f"{original_path.stem}_reencoded.mp4"
        
        ffmpeg_command = [
            "ffmpeg",
            "-i", str(original_renamed),
            "-c:v", "libx264",          # Video codec
            "-preset", "medium",         # Encoding speed/quality tradeoff
            "-crf", "23",               # Quality (lower = better, 18-28 reasonable range)
            "-c:a", "aac",              # Audio codec
            "-b:a", "128k",             # Audio bitrate
            "-movflags", "+faststart",  # Enable streaming
            "-y",                       # Overwrite output file
            str(reencoded_path)
        ]
        
        logger.info(f"Running ffmpeg: {' '.join(ffmpeg_command)}")
        
        result = subprocess.run(
            ffmpeg_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        logger.info(f"✅ Video re-encoded: {reencoded_path}")
        
        # Get file sizes
        original_size = original_renamed.stat().st_size / (1024 * 1024)  # MB
        reencoded_size = reencoded_path.stat().st_size / (1024 * 1024)  # MB
        
        await message.answer(
            "✅ **Тест завершён успешно!**\n\n"
            f"📁 Оригинал:\n`{original_renamed}`\n"
            f"📦 Размер: {original_size:.2f} МБ\n\n"
            f"📁 Перекодированный:\n`{reencoded_path}`\n"
            f"📦 Размер: {reencoded_size:.2f} МБ\n\n"
            f"💾 Разница: {original_size - reencoded_size:.2f} МБ "
            f"({((original_size - reencoded_size) / original_size * 100):.1f}%)\n\n"
            "⚠️ Файлы НЕ удалены, можешь их проверить!",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Test download failed: {e}")
        await message.answer(
            f"❌ **Ошибка теста:**\n`{str(e)}`\n\n"
            "Проверь логи для деталей.",
            parse_mode="Markdown"
        )
