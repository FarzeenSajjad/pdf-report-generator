#!/bin/bash
# Fires two POST /reports back to back and shows both responses carry the same id.
# Run this while the server is up: uvicorn app:app --port 8000

echo "First POST:"
curl -s -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{}'
echo
echo
echo "Second POST (same day, no force):"
curl -s -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{}'
echo
echo
echo "Force a new one:"
curl -s -X POST http://127.0.0.1:8000/reports -H "Content-Type: application/json" -d '{"force": true}'
echo
