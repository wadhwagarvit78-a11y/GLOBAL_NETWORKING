#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Starting ReferralCircle Platform on http://localhost:8000 ..."
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
