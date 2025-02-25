from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
import uvicorn

# Inisialisasi FastAPI
app = FastAPI(
    title="LangChain Service - OpenAI",
    description="Microservice untuk rekomendasi IT Asset Management menggunakan OpenAI GPT",
    version="1.0.0"
)

# Middleware CORS (Jika Diperlukan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register router dari routes.py
app.include_router(router)

# Endpoint Health Check
@app.get("/")
async def root():
    return {"message": "LangChain Service is Running"}

# Menjalankan Server Uvicorn
if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
