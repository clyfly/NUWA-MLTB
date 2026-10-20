#!/bin/bash
set -e

source .venv/bin/activate

echo "=== NUWA-MLTB Startup ==="
echo "Running updater..."
python3 update.py

echo "Starting bot..."
exec python3 -m bot
