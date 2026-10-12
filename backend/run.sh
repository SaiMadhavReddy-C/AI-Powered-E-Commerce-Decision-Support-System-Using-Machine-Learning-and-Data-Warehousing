#!/usr/bin/env bash
set -e

# ShopQ Backend Startup Script
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$DIR"

echo "=================================================="
echo " Starting ShopQ Backend Server"
echo "=================================================="

# Check if venv exists
if [ -d "venv" ]; then
    echo "Activating virtualenv..."
    source venv/bin/activate
fi

export PYTHONPATH="$DIR:$PYTHONPATH"

# Run Uvicorn Server
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
