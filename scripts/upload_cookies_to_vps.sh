#!/bin/bash
# Quick upload cookies to VPS

# Configuration
LOCAL_COOKIES="/Users/korso/Documents/projects/sly-fox-tunes/youtube_cookies.txt"
REMOTE_USER="root"
REMOTE_HOST="debian"  # Change to your VPS hostname or IP
REMOTE_PATH="/root/projects/sly-fox-tunes/youtube_cookies.txt"

echo "Uploading fresh cookies to VPS..."
echo "Local: $LOCAL_COOKIES"
echo "Remote: $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
echo ""

# Check if local file exists
if [ ! -f "$LOCAL_COOKIES" ]; then
    echo "❌ Error: Local cookies file not found!"
    exit 1
fi

# Show local file info
echo "Local file info:"
ls -lh "$LOCAL_COOKIES"
echo ""

# Upload
if scp "$LOCAL_COOKIES" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"; then
    echo ""
    echo "✅ Upload successful!"
    echo ""
    echo "Now on VPS run:"
    echo "  pkill -9 -f 'python main.py'"
    echo "  uv run python main.py"
else
    echo ""
    echo "❌ Upload failed!"
    echo ""
    echo "Manual command:"
    echo "  scp $LOCAL_COOKIES $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH"
fi
