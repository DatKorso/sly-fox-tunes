"""Inline keyboards for bot."""


from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def get_format_keyboard(url: str) -> InlineKeyboardMarkup:
    """
    Create inline keyboard for format selection.

    Note: URL is now stored in FSM state, not in callback_data.
    This avoids Telegram's 64-byte callback_data limit.

    Args:
        url: YouTube URL (not used, kept for API compatibility)

    Returns:
        InlineKeyboardMarkup with Video and Audio buttons
    """
    buttons = [
        [
            InlineKeyboardButton(text="🎬 Видео", callback_data="dl:video"),
            InlineKeyboardButton(text="🎵 Аудио", callback_data="dl:audio"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
