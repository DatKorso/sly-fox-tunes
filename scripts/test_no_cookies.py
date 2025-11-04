#!/usr/bin/env python3
"""
Test script to verify no-cookies bypass works.
Tests multiple video types without cookies.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.downloader import get_video_info
from loguru import logger


async def test_video(url: str, description: str) -> bool:
    """Test a single video URL."""
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing: {description}")
    logger.info(f"URL: {url}")
    logger.info(f"{'='*60}")
    
    try:
        info = await get_video_info(url)
        logger.success(f"✅ SUCCESS!")
        logger.info(f"   Title: {info['title']}")
        logger.info(f"   Duration: {info['duration']}s")
        logger.info(f"   Uploader: {info['uploader']}")
        return True
    except Exception as e:
        logger.error(f"❌ FAILED: {e}")
        return False


async def main():
    """Run tests on various video types."""
    # Remove cookies file if exists to test without cookies
    cookies_file = Path("youtube_cookies.txt")
    cookies_backup = Path("youtube_cookies.txt.test_backup")
    
    cookies_existed = cookies_file.exists()
    if cookies_existed:
        cookies_file.rename(cookies_backup)
        logger.warning("📦 Temporarily moved cookies file to test without cookies")
    else:
        logger.info("✓ No cookies file found - testing in cookieless mode")
    
    logger.info("\n" + "="*60)
    logger.info("🧪 NO-COOKIES BYPASS TEST SUITE")
    logger.info("="*60)
    
    # Test cases
    test_cases = [
        ("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "Classic video (Rick Roll)"),
        ("https://www.youtube.com/shorts/lATYVBJzfQ8", "YouTube Shorts"),
        ("https://www.youtube.com/watch?v=M_lxIiJ8ck4", "Previously problematic video"),
        ("https://www.youtube.com/watch?v=jNQXAC9IVRw", "Popular music video"),
    ]
    
    results = []
    for url, description in test_cases:
        success = await test_video(url, description)
        results.append((description, success))
        await asyncio.sleep(1)  # Be nice to YouTube
    
    # Restore cookies file
    if cookies_existed:
        cookies_backup.rename(cookies_file)
        logger.info("\n📦 Restored cookies file")
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("📊 TEST SUMMARY")
    logger.info("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        logger.info(f"{status} - {description}")
    
    logger.info("")
    logger.info(f"Success rate: {passed}/{total} ({100*passed//total}%)")
    
    if passed == total:
        logger.success("\n🎉 All tests passed! No-cookies bypass is working!")
    elif passed >= total * 0.75:
        logger.warning(f"\n⚠️  Most tests passed ({passed}/{total}), acceptable rate")
    else:
        logger.error(f"\n❌ Too many failures ({total-passed}/{total}), needs investigation")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
