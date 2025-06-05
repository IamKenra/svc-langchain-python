import os
import requests
import logging
from dotenv import load_dotenv
from groq import Groq  # Import library Groq jika tersedia

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_url = os.getenv("GROQ_API_URL", "http://localhost:8000")  # Default ke localhost jika tidak ada
        self.model_name = os.getenv("GROQ_MODEL", "qwen2.5-coder:7b")
        self.api_key = os.getenv("GROQ_API_KEY")  # API key untuk otentikasi

        if not self.api_url:
            raise ValueError("ERROR: GROQ_API_URL tidak ditemukan di environment variables!")

        if not self.api_key:
            raise ValueError("ERROR: GROQ_API_KEY tidak ditemukan di environment variables!")

        logger.info(f"Using hosted Groq model at: {self.api_url}, model: {self.model_name}")

    def predict(self, prompt: str):
        logger.info(f"Sending request to Groq API with model {self.model_name}: {prompt}")

        try:
            # Kirim permintaan ke Groq API
            response = requests.post(
                f"{self.api_url}/v1/predict",  # Endpoint Groq API
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "temperature": 0.2,
                    "top_p": 0.8
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"  # Gunakan API key untuk otentikasi
                },
                timeout=1000
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("output", "No response from model")  # Sesuaikan dengan respons Groq API
            return generated_text.strip()

        except requests.exceptions.Timeout:
            logger.error(f"Error: Request to Groq API timed out")
            return "Error: Groq API timed out"

        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing Groq API: {e}")
            return "Error processing request"

llm_client = LLMClient()