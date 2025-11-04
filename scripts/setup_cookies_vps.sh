#!/bin/bash
# VPS Cookies Setup and Verification Script
# For servers without GUI browser

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
COOKIES_FILE="$PROJECT_DIR/youtube_cookies.txt"

echo "=========================================="
echo "VPS YouTube Cookies Setup"
echo "=========================================="
echo ""

# Function to check if cookies file exists
check_cookies_file() {
    if [ -f "$COOKIES_FILE" ]; then
        echo "✓ Cookies file found: $COOKIES_FILE"
        
        # Check if it's not empty
        if [ -s "$COOKIES_FILE" ]; then
            local line_count=$(wc -l < "$COOKIES_FILE")
            echo "  Lines: $line_count"
            
            # Check for YouTube cookies
            if grep -q "youtube.com" "$COOKIES_FILE"; then
                echo "  ✓ Contains YouTube cookies"
                return 0
            else
                echo "  ✗ No YouTube cookies found"
                return 1
            fi
        else
            echo "  ✗ File is empty"
            return 1
        fi
    else
        echo "✗ Cookies file not found: $COOKIES_FILE"
        return 1
    fi
}

# Function to test cookies with yt-dlp
test_cookies() {
    echo ""
    echo "Testing cookies with yt-dlp..."
    echo ""
    
    cd "$PROJECT_DIR"
    
    # Try to extract info from a known problematic video
    if uv run python scripts/test_ytdlp_config.py "https://www.youtube.com/watch?v=M_lxIiJ8ck4" 2>&1 | grep -q "Successfully extracted"; then
        echo ""
        echo "=========================================="
        echo "✓ SUCCESS! Cookies are working!"
        echo "=========================================="
        return 0
    else
        echo ""
        echo "=========================================="
        echo "✗ FAILED! Cookies are not working"
        echo "=========================================="
        return 1
    fi
}

# Function to show upload instructions
show_upload_instructions() {
    local server_user="${USER}"
    local server_host=$(hostname -f 2>/dev/null || hostname)
    local server_path="$PROJECT_DIR/youtube_cookies.txt"
    
    echo ""
    echo "=========================================="
    echo "How to upload cookies file from local machine:"
    echo "=========================================="
    echo ""
    echo "1. On your LOCAL machine (with GUI browser):"
    echo "   a) Install browser extension:"
    echo "      Chrome: https://chromewebstore.google.com/detail/cclelndahbckbenkjhflpdbgdldlbecc"
    echo "      Firefox: https://addons.mozilla.org/firefox/addon/cookies-txt/"
    echo ""
    echo "   b) Login to YouTube in your browser"
    echo ""
    echo "   c) Open any YouTube video"
    echo ""
    echo "   d) Click extension icon → 'Export' → Save as 'youtube_cookies.txt'"
    echo ""
    echo "2. Upload to this server:"
    echo "   scp youtube_cookies.txt ${server_user}@${server_host}:${server_path}"
    echo ""
    echo "3. Run this script again to verify"
    echo ""
    echo "=========================================="
    echo ""
}

# Function to check .env configuration
check_env_config() {
    local env_file="$PROJECT_DIR/.env"
    
    echo ""
    echo "Checking .env configuration..."
    
    if [ ! -f "$env_file" ]; then
        echo "✗ .env file not found!"
        echo "  Create it from .env.example:"
        echo "  cp .env.example .env"
        return 1
    fi
    
    if grep -q "^COOKIES_FILE=" "$env_file"; then
        local cookie_path=$(grep "^COOKIES_FILE=" "$env_file" | cut -d'=' -f2)
        echo "✓ COOKIES_FILE configured: $cookie_path"
        return 0
    else
        echo "⚠ COOKIES_FILE not configured in .env"
        echo "  Add this line to .env:"
        echo "  COOKIES_FILE=youtube_cookies.txt"
        return 1
    fi
}

# Main execution
echo "Project directory: $PROJECT_DIR"
echo ""

# Step 1: Check if cookies file exists
if check_cookies_file; then
    # Step 2: Check .env configuration
    check_env_config
    
    # Step 3: Test cookies
    if test_cookies; then
        echo ""
        echo "✓ Everything is configured correctly!"
        echo "  Your bot should work without 'not a bot' errors."
        exit 0
    else
        echo ""
        echo "⚠ Cookies file exists but doesn't work."
        echo "  Possible reasons:"
        echo "  1. Cookies have expired (YouTube rotates them periodically)"
        echo "  2. Cookies weren't exported while logged in to YouTube"
        echo "  3. Cookies file format is incorrect"
        echo ""
        echo "Solution: Export fresh cookies from your browser"
        show_upload_instructions
        exit 1
    fi
else
    echo ""
    echo "⚠ Cookies file is missing or invalid"
    show_upload_instructions
    exit 1
fi
