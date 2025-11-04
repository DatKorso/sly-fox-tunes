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
    Uses multiple fallback strategies to avoid bot detection.
    
    Returns:
        Dictionary with base yt-dlp options
    """
    from config.settings import settings
    
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        # Anti-bot measures
        "nocheckcertificate": True,
        "prefer_insecure": False,
        
        # Enhanced extractor arguments for better bot evasion
        "extractor_args": {
            "youtube": {
                # Use multiple clients as fallback (ios works without cookies often)
                "player_client": ["ios", "android", "web"],
                "player_skip": ["webpage", "configs"],
                # Skip signature decryption issues
                "skip": ["dash", "hls"],
            }
        },
        
        # Mimic real iOS device (often bypasses bot detection)
        "http_headers": {
            "User-Agent": "com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)",
            "Accept": "*/*",
            "Accept-Language": "en-us,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "X-Youtube-Client-Name": "5",
            "X-Youtube-Client-Version": "19.09.3",
        },
        
        # Additional options to avoid restrictions
        "age_limit": None,  # Don't filter by age
        "geo_bypass": True,  # Try to bypass geo restrictions
        "no_check_certificate": True,
    }
    
    # Priority 1: Use cookies from browser (most reliable)
    if settings.cookies_from_browser:
        opts["cookiesfrombrowser"] = (settings.cookies_from_browser,)
        logger.info(f"Using cookies from browser: {settings.cookies_from_browser}")
    # Priority 2: Use cookies file
    elif settings.cookies_file and settings.cookies_file.exists():
        opts["cookiefile"] = str(settings.cookies_file)
        logger.info(f"Using cookies file: {settings.cookies_file}")
    elif settings.cookies_file:
        logger.warning(f"Cookies file not found: {settings.cookies_file}")
    else:
        logger.info("No cookies configured. Using iOS client fallback for bot detection bypass.")
    
    return opts


def _get_fallback_ydl_opts(client_type: str = "ios") -> dict[str, Any]:
    """
    Get yt-dlp options with specific client fallback.
    Used when primary method fails.
    
    Args:
        client_type: Client to use ("ios", "android", "mweb", "tv_embedded")
    
    Returns:
        Dictionary with yt-dlp options for specific client
    """
    from config.settings import settings
    
    # Client-specific configurations
    client_configs = {
        "ios": {
            "player_client": ["ios"],
            "user_agent": "com.google.ios.youtube/19.09.3 (iPhone14,3; U; CPU iOS 15_6 like Mac OS X)",
            "client_name": "5",
            "client_version": "19.09.3",
        },
        "android": {
            "player_client": ["android"],
            "user_agent": "com.google.android.youtube/19.09.37 (Linux; U; Android 11) gzip",
            "client_name": "3", 
            "client_version": "19.09.37",
        },
        "mweb": {
            "player_client": ["mweb"],
            "user_agent": "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "client_name": "2",
            "client_version": "2.20240111.09.00",
        },
        "tv_embedded": {
            "player_client": ["tv_embedded"],
            "user_agent": "Mozilla/5.0 (PlayStation 4 5.55) AppleWebKit/601.2 (KHTML, like Gecko)",
            "client_name": "85",
            "client_version": "2.0",
        },
    }
    
    config = client_configs.get(client_type, client_configs["ios"])
    
    opts: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": config["player_client"],
                "player_skip": ["webpage", "configs"],
            }
        },
        "http_headers": {
            "User-Agent": config["user_agent"],
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
        },
    }
    
    logger.info(f"Using fallback client: {client_type}")
    return opts


async def get_video_info(url: str) -> dict[str, Any]:
    """
    Extract video information from YouTube URL.
    Uses multiple fallback strategies if primary method fails.

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
        DownloadError: If video info cannot be extracted with any method
    """
    # Try primary method first
    ydl_opts = _get_base_ydl_opts()
    ydl_opts.update({
        "extract_flat": False,
    })

    logger.info(f"Extracting video info from: {url}")
    
    # Fallback clients to try if primary fails
    fallback_clients = ["ios", "android", "mweb", "tv_embedded"]
    
    # Try primary method
    try:
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

    except Exception as primary_error:
        logger.warning(f"Primary method failed: {primary_error}")
        
        # Try fallback clients
        for client in fallback_clients:
            try:
                logger.info(f"Trying fallback client: {client}")
                fallback_opts = _get_fallback_ydl_opts(client)
                fallback_opts.update({"extract_flat": False})
                
                loop = asyncio.get_event_loop()
                info = await loop.run_in_executor(
                    None, lambda: _extract_info_sync(url, fallback_opts)
                )

                result = {
                    "title": info.get("title", "Unknown"),
                    "duration": info.get("duration", 0),
                    "thumbnail": info.get("thumbnail", ""),
                    "uploader": info.get("uploader", "Unknown"),
                    "view_count": info.get("view_count", 0),
                }

                logger.success(f"Fallback {client} succeeded! Extracted: {result['title']}")
                return result

            except Exception as e:
                logger.warning(f"Fallback {client} failed: {e}")
                continue
        
        # All methods failed
        logger.error(f"All extraction methods failed for: {url}")
        raise DownloadError(
            f"Could not get video information after trying all methods. "
            f"Last error: {primary_error}"
        ) from primary_error


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
