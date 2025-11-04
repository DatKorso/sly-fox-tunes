"""File manager service for handling temporary files."""

from __future__ import annotations

import asyncio
import shutil
from pathlib import Path

from loguru import logger

from config import settings


def get_user_temp_dir(user_id: int) -> Path:
    """
    Get or create temporary directory for a specific user.

    Args:
        user_id: Telegram user ID

    Returns:
        Path to user's temporary directory

    Example:
        >>> path = get_user_temp_dir(123456)
        >>> print(path)
        temp/123456
    """
    user_dir = settings.temp_dir / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    logger.debug(f"User temp directory for {user_id}: {user_dir}")
    return user_dir


async def cleanup_file(file_path: Path) -> None:
    """
    Asynchronously delete a file or directory with logging.

    Args:
        file_path: Path to the file or directory to delete

    Note:
        Does not raise an error if file/directory doesn't exist.
        Handles both files and directories appropriately.
    """
    if not file_path.exists():
        logger.debug(f"Path does not exist, skipping cleanup: {file_path}")
        return

    try:
        logger.info(f"Cleaning up: {file_path}")

        # Run deletion in executor to avoid blocking
        loop = asyncio.get_event_loop()
        
        if file_path.is_file():
            # Delete file
            await loop.run_in_executor(None, file_path.unlink)
            logger.info(f"Successfully deleted file: {file_path}")
        elif file_path.is_dir():
            # Delete directory and its contents
            await loop.run_in_executor(None, shutil.rmtree, file_path)
            logger.info(f"Successfully deleted directory: {file_path}")

    except Exception as e:
        logger.error(f"Failed to delete {file_path}: {e}")
        # Don't raise - cleanup failures shouldn't crash the bot


async def cleanup_user_dir(user_id: int) -> None:
    """
    Asynchronously delete all files in user's temporary directory.

    Removes the entire user directory and all its contents.

    Args:
        user_id: Telegram user ID

    Note:
        Does not raise an error if directory doesn't exist.
    """
    user_dir = settings.temp_dir / str(user_id)

    if not user_dir.exists():
        logger.debug(f"User directory does not exist, skipping cleanup: {user_dir}")
        return

    try:
        logger.info(f"Cleaning up user directory: {user_dir}")

        # Count files before deletion for logging
        file_count = len(list(user_dir.rglob("*")))

        # Run directory deletion in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, shutil.rmtree, user_dir)

        logger.info(
            f"Successfully deleted user directory {user_dir} "
            f"({file_count} files/folders removed)"
        )

    except Exception as e:
        logger.error(f"Failed to delete user directory {user_dir}: {e}")
        # Don't raise - cleanup failures shouldn't crash the bot


async def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes asynchronously.

    Args:
        file_path: Path to the file

    Returns:
        File size in bytes

    Raises:
        FileNotFoundError: If file doesn't exist
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    loop = asyncio.get_event_loop()
    stat = await loop.run_in_executor(None, file_path.stat)
    return stat.st_size


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB", "234 KB")

    Example:
        >>> format_file_size(1536)
        '1.5 KB'
        >>> format_file_size(1048576)
        '1.0 MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


class FileManager:
    """Service class wrapper for file manager functions."""

    def get_user_temp_dir(self, user_id: int) -> Path:
        """Get user temp directory."""
        return get_user_temp_dir(user_id)

    async def cleanup_file(self, file_path: Path) -> None:
        """Clean up a file."""
        await cleanup_file(file_path)

    async def cleanup_user_dir(self, user_id: int) -> None:
        """Clean up user directory."""
        await cleanup_user_dir(user_id)

    async def get_file_size(self, file_path: Path) -> int:
        """Get file size."""
        return await get_file_size(file_path)

    def format_file_size(self, size_bytes: int) -> str:
        """Format file size."""
        return format_file_size(size_bytes)
