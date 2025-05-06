import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_url = os.getenv("OLLAMA_API_KEY")
        self.model_name = os.getenv("OLLAMA_MODEL", "qwen2.5-coder:7b")

        if not self.api_url:
            raise ValueError("ERROR: OLLAMA_API_URL tidak ditemukan di environment variables!")

        logger.info(f"Using hosted Ollama model at: {self.api_url}, model: {self.model_name}")

    def predict(self, prompt: str):
        logger.info(f"Sending request to Ollama API with model {self.model_name}: {prompt}")

        try:
            response = requests.post(
                self.api_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.2,
                    "top_p": 0.8 
                },
                headers={"Content-Type": "application/json"},
                timeout=1000 
            )
            response.raise_for_status()
            result = response.json()
            generated_text = result.get("response", "No response from model")
            generated_text = generated_text.replace("<think>", "").replace("</think>", "").strip()

            return generated_text

        except requests.exceptions.Timeout:
            logger.error(f"Error: Request to Ollama API timed out")
            return "Error: Ollama API timed out"

        except requests.exceptions.RequestException as e:
            logger.error(f"Error accessing Ollama API: {e}")
            return "Error processing request"

llm_client = LLMClient()
