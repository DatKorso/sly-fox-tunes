"""Test script to verify cookies configuration."""

from pathlib import Path
from config.settings import settings
from services.downloader import _get_base_ydl_opts


def test_cookies_config():
    """Test that cookies configuration is loaded correctly."""
    print("=" * 60)
    print("Testing Cookies Configuration")
    print("=" * 60)
    
    # Check settings
    print(f"\n1. Settings.cookies_file: {settings.cookies_file}")
    
    if settings.cookies_file:
        cookies_path = Path(settings.cookies_file)
        print(f"   Type: {type(settings.cookies_file)}")
        print(f"   Exists: {cookies_path.exists()}")
        
        if cookies_path.exists():
            print(f"   Size: {cookies_path.stat().st_size} bytes")
            print("   ✓ Cookies file is accessible")
        else:
            print("   ⚠ Cookies file path is set but file doesn't exist")
            print(f"   Expected location: {cookies_path.absolute()}")
    else:
        print("   ℹ No cookies file configured (optional)")
    
    # Check yt-dlp options
    print("\n2. yt-dlp base options:")
    opts = _get_base_ydl_opts()
    
    for key, value in opts.items():
        print(f"   {key}: {value}")
    
    if 'cookiefile' in opts:
        print("\n   ✓ Cookies will be used for YouTube downloads")
    else:
        print("\n   ℹ Downloads will work without cookies (may fail on some videos)")
    
    print("\n" + "=" * 60)
    print("Configuration check complete!")
    print("=" * 60)


if __name__ == "__main__":
    test_cookies_config()
