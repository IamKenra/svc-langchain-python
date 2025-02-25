#!/bin/bash

# Periksa apakah nodemon sudah terinstal
if ! command -v nodemon &> /dev/null
then
    echo "Nodemon tidak ditemukan, menginstalnya sekarang..."
    npm install -g nodemon
fi

echo "Menjalankan LangChain Service dengan Nodemon..."
nodemon --exec "python3 -m uvicorn src.main:app --host 0.0.0.0 --port 80 --reload"
