"""YouTube downloader service using yt-dlp."""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path
from typing import Any

import yt_dlp
from loguru import logger


class DownloadError(Exception):
    """Custom exception for download errors."""

    pass


def _get_base_ydl_opts() -> dict[str, Any]:
    """
    Get base yt-dlp options including cookies if configured.
    
    Returns:
        Dictionary with base yt-dlp options
    """
    from config.settings import settings
    
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
    }
    
    # Add cookies file if configured
    if settings.cookies_file and settings.cookies_file.exists():
        opts["cookiefile"] = str(settings.cookies_file)
        logger.info(f"Using cookies file: {settings.cookies_file}")
    elif settings.cookies_file:
        logger.warning(f"Cookies file not found: {settings.cookies_file}")
    
    return opts


async def get_video_info(url: str) -> dict[str, Any]:
    """
    Extract video information from YouTube URL.

    Args:
        url: YouTube video URL

    Returns:
        Dictionary with video info containing:
            - title: Video title
            - duration: Duration in seconds
            - thumbnail: Thumbnail URL
            - uploader: Channel name
            - view_count: Number of views

    Raises:
        DownloadError: If video info cannot be extracted
    """
    ydl_opts = _get_base_ydl_opts()
    ydl_opts.update({
        "extract_flat": False,
    })

    try:
        logger.info(f"Extracting video info from: {url}")

        # Run yt-dlp in executor to avoid blocking
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: _extract_info_sync(url, ydl_opts))

        result = {
            "title": info.get("title", "Unknown"),
            "duration": info.get("duration", 0),
            "thumbnail": info.get("thumbnail", ""),
            "uploader": info.get("uploader", "Unknown"),
            "view_count": info.get("view_count", 0),
        }

        logger.info(f"Successfully extracted info for: {result['title']}")
        return result

    except Exception as e:
        logger.error(f"Failed to extract video info: {e}")
        raise DownloadError(f"Could not get video information: {e}") from e


def _extract_info_sync(url: str, ydl_opts: dict[str, Any]) -> dict[str, Any]:
    """Synchronous helper to extract info with yt-dlp."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(url, download=False)


async def download_video(url: str, output_path: Path) -> Path:
    """
    Download video from YouTube in MP4 format.

    Downloads video with 720p quality (or best available if 720p not available).
    Video is re-encoded with FFmpeg to ensure Telegram compatibility.

    Args:
        url: YouTube video URL
        output_path: Path where to save the downloaded video

    Returns:
        Path to the downloaded video file

    Raises:
        DownloadError: If download fails
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Temporary file for initial download
    temp_download_path = output_path.with_name(f"{output_path.name}_temp")
    
    ydl_opts = _get_base_ydl_opts()
    ydl_opts.update({
        # Download best quality video+audio
        "format": "bestvideo[height<=720]+bestaudio/best[height<=720]",
        "outtmpl": str(temp_download_path),
        "merge_output_format": "mp4",
    })

    try:
        logger.info(f"Starting video download from: {url}")
        logger.info(f"Output path: {output_path}")

        # Run yt-dlp in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: _download_sync(url, ydl_opts))

        # yt-dlp may add .mp4 extension if not present
        if not temp_download_path.exists():
            temp_download_path = temp_download_path.with_suffix(".mp4")
            if not temp_download_path.exists():
                raise DownloadError("Downloaded file not found")

        logger.info(f"Downloaded raw video to: {temp_download_path}")
        
        # Re-encode video with FFmpeg to ensure Telegram compatibility
        final_output_path = output_path.with_suffix(".mp4")
        logger.info(f"Starting re-encoding for Telegram compatibility...")
        logger.info(f"Input file: {temp_download_path}")
        logger.info(f"Output file: {final_output_path}")
        
        try:
            await loop.run_in_executor(
                None, 
                lambda: _reencode_for_telegram(temp_download_path, final_output_path)
            )
            logger.info(f"Re-encoding completed successfully")
        except Exception as e:
            logger.error(f"Re-encoding failed: {e}")
            raise
        
        # Clean up temporary file
        if temp_download_path.exists():
            temp_download_path.unlink()
            logger.info(f"Removed temporary file: {temp_download_path}")

        logger.info(f"Successfully processed video to: {final_output_path}")
        return final_output_path

    except Exception as e:
        logger.error(f"Failed to download video: {e}")
        raise DownloadError(f"Could not download video: {e}") from e


async def download_audio(url: str, output_path: Path) -> Path:
    """
    Download audio from YouTube in MP3 format.

    Downloads audio with 192kbps quality.

    Args:
        url: YouTube video URL
        output_path: Path where to save the downloaded audio

    Returns:
        Path to the downloaded audio file

    Raises:
        DownloadError: If download fails
    """
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ydl_opts = _get_base_ydl_opts()
    ydl_opts.update({
        "format": "bestaudio/best",
        "outtmpl": str(output_path),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    })

    try:
        logger.info(f"Starting audio download from: {url}")
        logger.info(f"Output path: {output_path}")

        # Run yt-dlp in executor to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: _download_sync(url, ydl_opts))

        # yt-dlp will add .mp3 extension after conversion
        output_path_mp3 = output_path.with_suffix(".mp3")
        if not output_path_mp3.exists() and output_path.exists():
            # If original file exists but not mp3, use original
            output_path_mp3 = output_path
        elif not output_path_mp3.exists():
            raise DownloadError("Downloaded file not found")

        logger.info(f"Successfully downloaded audio to: {output_path_mp3}")
        return output_path_mp3

    except Exception as e:
        logger.error(f"Failed to download audio: {e}")
        raise DownloadError(f"Could not download audio: {e}") from e


def _reencode_for_telegram(input_path: Path, output_path: Path) -> None:
    """
    Re-encode video with FFmpeg to ensure Telegram compatibility.
    
    Uses H.264 video codec and AAC audio codec with yuv420p pixel format.
    This ensures the video will play correctly in Telegram on all devices.
    """
    logger.info(f"Starting FFmpeg re-encoding...")
    logger.info(f"Input: {input_path} (exists: {input_path.exists()})")
    logger.info(f"Output: {output_path}")
    
    cmd = [
        "ffmpeg",
        "-i", str(input_path),
        "-c:v", "libx264",           # H.264 video codec
        "-preset", "fast",            # Encoding speed
        "-crf", "23",                 # Quality (18-28, lower = better)
        "-c:a", "aac",                # AAC audio codec
        "-b:a", "192k",               # Audio bitrate
        "-movflags", "+faststart",    # Enable streaming
        "-pix_fmt", "yuv420p",        # Pixel format for compatibility
        "-y",                         # Overwrite output file
        str(output_path)
    ]
    
    logger.info(f"FFmpeg command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            text=True
        )
        logger.info(f"FFmpeg completed. Output file exists: {output_path.exists()}")
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            logger.info(f"Output file size: {size_mb:.2f} MB")
        logger.info("Video re-encoded successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        raise DownloadError(f"Failed to re-encode video: {e.stderr}") from e


def _download_sync(url: str, ydl_opts: dict[str, Any]) -> None:
    """Synchronous helper to download with yt-dlp."""
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])


class DownloaderService:
    """Service class wrapper for downloader functions."""

    async def get_video_info(self, url: str) -> dict[str, Any]:
        """Get video information."""
        return await get_video_info(url)

    async def download_video(self, url: str, output_path: Path) -> Path:
        """Download video."""
        return await download_video(url, output_path)

    async def download_audio(self, url: str, output_path: Path) -> Path:
        """Download audio."""
        return await download_audio(url, output_path)
