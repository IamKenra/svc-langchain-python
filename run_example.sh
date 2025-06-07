# Periksa apakah nodemon sudah terinstal
if ! command -v nodemon &> /dev/null
then
    echo "Nodemon tidak ditemukan, menginstalnya sekarang..."
    npm install -g nodemon
fi

PORT=3001
PID=$(lsof -ti tcp:$PORT)
if [ -n "$PID" ]; then
    echo "Membunuh proses pada port $PORT (PID: $PID)..."
    kill -9 $PID
fi

echo "Menjalankan LangChain Service dengan Nodemon..."
nodemon --exec "python3 -m uvicorn src.main:app --host 0.0.0.0 --port 3001 --reload"