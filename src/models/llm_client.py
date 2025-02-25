import os
import requests
import logging
from dotenv import load_dotenv

# Memuat variabel dari file .e
load_dotenv()

# Konfigurasi logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_KEY")
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

        if not self.api_url:
            raise ValueError("🚨 ERROR: OLLAMA_API_URL tidak ditemukan di environment variables!")

        logger.info(f"🔍 Using hosted Ollama model at: {self.api_url}, model: {self.model_name}")

    def predict(self, prompt: str):
        logger.info(f"🚀 Sending request to Ollama API with model {self.model_name}: {prompt}")

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                headers={"Content-Type": "application/json"},
                timeout=60  # Timeout lebih lama untuk model besar
            )
            response.raise_for_status()

            # Ambil response JSON
            result = response.json()

            # Cek apakah respons valid dan ambil hanya bagian teks jawaban
            generated_text = result.get("response", "No response from model")

            # Hapus <think> tags jika ada
            generated_text = generated_text.replace("<think>", "").replace("</think>", "").strip()

            return generated_text

        except requests.exceptions.Timeout:
            logger.error(f"❌ Error: Request to Ollama API timed out")
            return "Error: Ollama API timed out"

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Error accessing Ollama API: {e}")
            return "Error processing request"

# Inisialisasi instance LLM Client
llm_client = LLMClient()
