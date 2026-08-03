#!/bin/bash
cd "$(dirname "$0")"
python3 scripts/update_photos.py
echo ""
echo "Done. Press Enter to close this window..."
read
