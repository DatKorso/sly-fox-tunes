#!/usr/bin/env python3
"""
Test script to verify yt-dlp configuration with cookies.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import yt_dlp
from loguru import logger


def test_cookies_with_video(video_url: str, use_browser: str | None = None) -> None:
    """Test if cookies work with a specific video."""
    logger.info(f"Testing video: {video_url}")
    
    ydl_opts = {
        "quiet": False,
        "verbose": True,
        "nocheckcertificate": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "web"],
                "player_skip": ["webpage", "configs"],
            }
        },
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-us,en;q=0.5",
            "Sec-Fetch-Mode": "navigate",
        },
    }
    
    # Configure cookies source
    if use_browser:
        ydl_opts["cookiesfrombrowser"] = (use_browser,)
        logger.info(f"Using cookies from browser: {use_browser}")
    else:
        cookies_file = Path("youtube_cookies.txt")
        if not cookies_file.exists():
            logger.error(f"Cookies file not found: {cookies_file}")
            logger.info("Try using --browser option instead")
            return
        ydl_opts["cookiefile"] = str(cookies_file)
        logger.info(f"Using cookies file: {cookies_file}")
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info("Extracting video info...")
            info = ydl.extract_info(video_url, download=False)
            
            if info:
                logger.success("✓ Successfully extracted video info!")
                logger.info(f"  Title: {info.get('title')}")
                logger.info(f"  Duration: {info.get('duration')}s")
                logger.info(f"  Uploader: {info.get('uploader')}")
                logger.info(f"  Format count: {len(info.get('formats', []))}")
            else:
                logger.error("✗ Failed to extract video info")
                
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test yt-dlp configuration with cookies")
    parser.add_argument("url", nargs="?", default="https://www.youtube.com/watch?v=M_lxIiJ8ck4",
                       help="YouTube video URL to test")
    parser.add_argument("--browser", choices=["chrome", "firefox", "edge", "brave", "safari", "opera"],
                       help="Use cookies from browser instead of file")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("yt-dlp Configuration Test")
    logger.info("=" * 60)
    
    test_cookies_with_video(args.url, args.browser)
