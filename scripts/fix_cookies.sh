#!/bin/bash
# Quick fix script for YouTube "Sign in to confirm you're not a bot" error

set -e

echo "=========================================="
echo "YouTube Cookies Fix Script"
echo "=========================================="
echo ""

# Check if running on Linux or macOS
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    PLATFORM="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macos"
else
    echo "⚠️  Unknown platform: $OSTYPE"
    PLATFORM="unknown"
fi

echo "Platform: $PLATFORM"
echo ""

# Function to test configuration
test_config() {
    local browser=$1
    echo "Testing with browser: $browser"
    uv run python scripts/test_ytdlp_config.py --browser "$browser" "https://www.youtube.com/watch?v=M_lxIiJ8ck4"
}

# Offer solutions
echo "🔧 Available Solutions:"
echo ""
echo "1. Use cookies directly from browser (RECOMMENDED)"
echo "   - No manual export needed"
echo "   - Always fresh cookies"
echo "   - Works automatically"
echo ""
echo "2. Export fresh cookies file"
echo "   - Requires browser extension"
echo "   - Needs manual updates"
echo ""

read -p "Choose solution (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "Available browsers:"
        echo "  1) Chrome"
        echo "  2) Firefox"
        echo "  3) Edge"
        echo "  4) Brave"
        if [[ "$PLATFORM" == "macos" ]]; then
            echo "  5) Safari"
        fi
        echo ""
        read -p "Select browser (1-5): " browser_choice
        
        case $browser_choice in
            1) BROWSER="chrome" ;;
            2) BROWSER="firefox" ;;
            3) BROWSER="edge" ;;
            4) BROWSER="brave" ;;
            5) BROWSER="safari" ;;
            *) echo "Invalid choice"; exit 1 ;;
        esac
        
        echo ""
        echo "Testing configuration with $BROWSER..."
        test_config "$BROWSER"
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✓ Success! Now update your .env file:"
            echo ""
            echo "  COOKIES_FROM_BROWSER=$BROWSER"
            echo ""
            echo "Add this line to your .env file and restart the bot."
        fi
        ;;
        
    2)
        echo ""
        echo "📋 Instructions to export cookies:"
        echo ""
        echo "1. Install browser extension:"
        if [[ "$PLATFORM" == "linux" ]]; then
            echo "   Chrome: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
            echo "   Firefox: https://addons.mozilla.org/firefox/addon/cookies-txt/"
        else
            echo "   Chrome: https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
            echo "   Firefox: https://addons.mozilla.org/firefox/addon/cookies-txt/"
        fi
        echo ""
        echo "2. Sign in to YouTube in your browser"
        echo "3. Open any YouTube video"
        echo "4. Click extension icon → Export cookies.txt"
        echo "5. Save as 'youtube_cookies.txt' in project root"
        echo "6. Update .env: COOKIES_FILE=youtube_cookies.txt"
        echo ""
        echo "See docs/COOKIES-UPDATE.md for detailed instructions"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac

echo ""
echo "Done!"
