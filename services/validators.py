"""URL validation utilities."""

from __future__ import annotations

import re


def is_youtube_url(text: str) -> bool:
    """
    Check if the given text is a valid YouTube URL.

    Supports the following formats:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtube.com/watch?v=VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/shorts/VIDEO_ID
    - http versions of above

    Args:
        text: Text to check

    Returns:
        True if text is a valid YouTube URL, False otherwise

    Examples:
        >>> is_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        True
        >>> is_youtube_url("https://youtu.be/dQw4w9WgXcQ")
        True
        >>> is_youtube_url("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        True
        >>> is_youtube_url("Not a URL")
        False
        >>> is_youtube_url("https://vimeo.com/123456")
        False
    """
    if not text or not isinstance(text, str):
        return False

    # YouTube URL patterns
    patterns = [
        # Standard youtube.com/watch?v= format
        r"^https?://(www\.)?youtube\.com/watch\?v=[\w-]{11}",
        # Mobile youtube format
        r"^https?://m\.youtube\.com/watch\?v=[\w-]{11}",
        # Short youtu.be format
        r"^https?://youtu\.be/[\w-]{11}",
        # YouTube Shorts format (www)
        r"^https?://(www\.)?youtube\.com/shorts/[\w-]{11}",
        # YouTube Shorts format (mobile)
        r"^https?://m\.youtube\.com/shorts/[\w-]{11}",
    ]

    # Check if text matches any of the patterns
    for pattern in patterns:
        if re.match(pattern, text):
            return True

    return False


def extract_video_id(url: str) -> str | None:
    """
    Extract video ID from YouTube URL.

    Args:
        url: YouTube URL

    Returns:
        Video ID if found, None otherwise

    Examples:
        >>> extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://youtu.be/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ")
        'dQw4w9WgXcQ'
        >>> extract_video_id("Not a URL")
        None
    """
    if not is_youtube_url(url):
        return None

    # Pattern for watch?v= format
    match = re.search(r"[?&]v=([\w-]{11})", url)
    if match:
        return match.group(1)

    # Pattern for youtu.be format
    match = re.search(r"youtu\.be/([\w-]{11})", url)
    if match:
        return match.group(1)

    # Pattern for YouTube Shorts format
    match = re.search(r"youtube\.com/shorts/([\w-]{11})", url)
    if match:
        return match.group(1)

    return None
