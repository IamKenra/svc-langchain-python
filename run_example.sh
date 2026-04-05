#!/bin/bash
export INTERNAL_API_KEY="dev-internal-api-key"

# Periksa apakah nodemon sudah terinstal
if ! command -v nodemon &> /dev/null
then
    echo "Nodemon not found, installing now.."
    npm install -g nodemon
fi

PORT=3001
PID=$(lsof -ti tcp:$PORT)
if [ -n "$PID" ]; then
    echo "Membunuh proses pada port $PORT (PID: $PID)..."
    kill -9 $PID
fi

echo "Menjalankan LangChain Service dengan Nodemon pada port ${PORT}..."
nodemon --exec "python3 -m uvicorn src.main:app --host 0.0.0.0 --port ${PORT} --reload"
