#!/bin/bash
# Upload YouTube cookies to remote server
# Usage: ./upload_cookies.sh <cookies_file> <remote_destination>
# Example: ./upload_cookies.sh youtube_cookies.txt root@example.com:/root/projects/sly-fox-tunes/

set -e

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <cookies_file> <remote_destination>"
    echo "Example: $0 youtube_cookies.txt user@vps:/root/projects/sly-fox-tunes/"
    exit 1
fi

COOKIES_FILE="$1"
REMOTE_DEST="$2"

# Check if cookies file exists
if [ ! -f "$COOKIES_FILE" ]; then
    echo "Error: Cookies file '$COOKIES_FILE' not found!"
    exit 1
fi

echo "Uploading cookies file to server..."
scp "$COOKIES_FILE" "$REMOTE_DEST"

echo "Setting proper permissions on remote server..."
# Extract server and path from remote destination
SERVER=$(echo "$REMOTE_DEST" | cut -d: -f1)
REMOTE_PATH=$(echo "$REMOTE_DEST" | cut -d: -f2)
COOKIES_FILENAME=$(basename "$COOKIES_FILE")

ssh "$SERVER" "chmod 600 ${REMOTE_PATH}${COOKIES_FILENAME}"

echo "✓ Cookies uploaded successfully!"
echo "Don't forget to add COOKIES_FILE=${COOKIES_FILENAME} to your .env file on the server"
