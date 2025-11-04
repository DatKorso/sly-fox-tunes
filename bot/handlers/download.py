"""Download handler for processing YouTube URLs and downloading media."""

from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile, Message
from loguru import logger

from bot.keyboards.inline import get_format_keyboard
from services.downloader import DownloaderService
from services.file_manager import FileManager
from services.validators import is_youtube_url

router = Router(name="download")

# Initialize services
downloader = DownloaderService()
file_manager = FileManager()


@router.message(F.text)
async def handle_text_message(message: Message) -> None:
    """
    Handle text messages - check if it's a YouTube URL.

    If URL is valid, show video info and format selection buttons.
    Otherwise, prompt user to send a YouTube link.
    """
    text = message.text or ""

    # Check if text is a YouTube URL
    if not is_youtube_url(text):
        await message.answer(
            "❌ Это не похоже на ссылку YouTube\n\n"
            "📎 Отправь мне ссылку на видео в формате:\n"
            "• https://youtube.com/watch?v=...\n"
            "• https://youtu.be/...\n\n"
            "💡 Используй /help для получения помощи"
        )
        return

    # Show "processing" message
    status_msg = await message.answer("🔍 Получаю информацию о видео...")

    try:
        # Get video info
        video_info = await downloader.get_video_info(text)

        # Format duration
        duration_str = _format_duration(video_info.get("duration", 0))

        # Prepare info message with hidden URL (using zero-width space)
        info_text = (
            f"📹 <b>{video_info.get('title', 'Без названия')}</b>\n\n"
            f"⏱ Длительность: {duration_str}\n"
            f"👤 Автор: {video_info.get('uploader', 'Неизвестно')}\n\n"
            f"Выбери формат для скачивания:\n"
            f"<span class='tg-spoiler'>{text}</span>"  # Hidden URL in spoiler
        )

        # Send info with format selection keyboard
        await status_msg.edit_text(info_text, parse_mode="HTML", reply_markup=get_format_keyboard(text))

        # Store URL in callback data context (will be available in callback)
        # For ULTRA-MVP we'll use message text to retrieve URL

    except Exception as e:
        logger.error(f"Error getting video info: {e}")
        await status_msg.edit_text(
            "❌ Не удалось получить информацию о видео\n\n"
            "Возможные причины:\n"
            "• Видео недоступно или удалено\n"
            "• Видео приватное\n"
            "• Проблемы с сетью\n\n"
            "Попробуй другую ссылку или повтори попытку позже"
        )


@router.callback_query(F.data == "dl:video")
async def handle_video_download(callback: CallbackQuery) -> None:
    """Handle video format selection and download."""
    await callback.answer()

    # Extract URL from message text (hidden in spoiler)
    if not callback.message or not callback.message.text:
        await callback.message.edit_text("❌ Не удалось найти ссылку. Отправь её заново.")
        return
    
    # Extract URL from spoiler tag in message
    import re
    url_match = re.search(r'https?://[^\s<]+', callback.message.text)
    if not url_match:
        await callback.message.edit_text("❌ Не удалось найти ссылку. Отправь её заново.")
        return
    
    url = url_match.group(0)
    user_id = callback.from_user.id

    # Update message to show download progress
    await callback.message.edit_text("⏬ Скачиваю видео...\n\n⏳ Это может занять некоторое время")

    temp_file = None
    try:
        # Create user temp directory
        user_temp_dir = file_manager.get_user_temp_dir(user_id)

        # Download video
        temp_file = await downloader.download_video(url, user_temp_dir)

        logger.info(f"Video downloaded: {temp_file}")

        # Update message
        await callback.message.edit_text("📤 Отправляю видео...")

        # Extract video metadata for Telegram
        import subprocess
        import json
        try:
            ffprobe_result = subprocess.run(
                [
                    "ffprobe",
                    "-v", "quiet",
                    "-print_format", "json",
                    "-show_format",
                    "-show_streams",
                    str(temp_file)
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            video_metadata = json.loads(ffprobe_result.stdout)
            
            # Find video stream
            video_stream = next(
                (s for s in video_metadata.get("streams", []) if s.get("codec_type") == "video"),
                {}
            )
            
            width = video_stream.get("width", 0)
            height = video_stream.get("height", 0)
            duration = int(float(video_metadata.get("format", {}).get("duration", 0)))
            
            logger.info(f"Video metadata: {width}x{height}, duration: {duration}s")
        except Exception as e:
            logger.warning(f"Could not extract video metadata: {e}")
            width = height = duration = 0

        # Send video to user with proper parameters
        video_file = FSInputFile(temp_file)
        await callback.message.answer_video(
            video=video_file,
            caption="✅ Видео готово!",
            supports_streaming=True,
            width=width if width > 0 else None,
            height=height if height > 0 else None,
            duration=duration if duration > 0 else None
        )

        # Delete status message
        await callback.message.delete()

        logger.info(f"Video sent to user {user_id}")

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при скачивании видео\n\n"
            "Возможные причины:\n"
            "• Файл слишком большой (>2 ГБ)\n"
            "• Проблемы с сетью\n"
            "• Видео недоступно\n\n"
            "Попробуй другое видео или повтори попытку позже"
        )

    finally:
        # Cleanup: always delete temporary file
        if temp_file:
            await file_manager.cleanup_file(temp_file)
            logger.info(f"Cleaned up temp file: {temp_file}")


@router.callback_query(F.data == "dl:audio")
async def handle_audio_download(callback: CallbackQuery) -> None:
    """Handle audio format selection and download."""
    await callback.answer()

    # Extract URL from message text (hidden in spoiler)
    if not callback.message or not callback.message.text:
        await callback.message.edit_text("❌ Не удалось найти ссылку. Отправь её заново.")
        return
    
    # Extract URL from spoiler tag in message
    import re
    url_match = re.search(r'https?://[^\s<]+', callback.message.text)
    if not url_match:
        await callback.message.edit_text("❌ Не удалось найти ссылку. Отправь её заново.")
        return
    
    url = url_match.group(0)
    user_id = callback.from_user.id

    # Update message to show download progress
    await callback.message.edit_text("⏬ Скачиваю аудио...\n\n⏳ Это может занять некоторое время")

    temp_file = None
    try:
        # Create user temp directory
        user_temp_dir = file_manager.get_user_temp_dir(user_id)

        # Download audio
        temp_file = await downloader.download_audio(url, user_temp_dir)

        logger.info(f"Audio downloaded: {temp_file}")

        # Update message
        await callback.message.edit_text("📤 Отправляю аудио...")

        # Send audio to user
        audio_file = FSInputFile(temp_file)
        await callback.message.answer_audio(audio=audio_file, caption="✅ Аудио готово!")

        # Delete status message
        await callback.message.delete()

        logger.info(f"Audio sent to user {user_id}")

    except Exception as e:
        logger.error(f"Error downloading audio: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при скачивании аудио\n\n"
            "Возможные причины:\n"
            "• Файл слишком большой (>2 ГБ)\n"
            "• Проблемы с сетью\n"
            "• Видео недоступно\n\n"
            "Попробуй другое видео или повтори попытку позже"
        )

    finally:
        # Cleanup: always delete temporary file
        if temp_file:
            await file_manager.cleanup_file(temp_file)
            logger.info(f"Cleaned up temp file: {temp_file}")


def _format_duration(seconds: int) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string like "3:45" or "1:23:45"
    """
    if seconds <= 0:
        return "0:00"

    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"
