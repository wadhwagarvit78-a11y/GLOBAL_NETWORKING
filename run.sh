#!/usr/bin/env bash
cd "$(dirname "$0")"

echo "================================================="
echo "  Starting ReferralCircle Platform..."
echo "  Opening http://localhost:8000 in your browser..."
echo "================================================="

# Automatically open browser in 1 second
(sleep 1 && (xdg-open http://localhost:8000 || python3 -m webbrowser http://localhost:8000 || google-chrome http://localhost:8000) >/dev/null 2>&1) &

# Start the web server
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
