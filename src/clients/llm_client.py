import os
import requests
import logging
from dotenv import load_dotenv
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import RunnableLambda

load_dotenv()

logger = logging.getLogger(__name__)

class LLMClient:
    def __init__(self):
        self.api_url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai")
        self.model_name = os.getenv("GROQ_MODEL", "llama3-70b-8192")
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("ERROR: GROQ_API_KEY tidak ditemukan!")

        logger.info(f"Using Groq Cloud at: {self.api_url}, model: {self.model_name}")

    def predict(self, prompt: str) -> str:
        logger.info(f"Sending request to Groq API with model {self.model_name}: text='{prompt[:80]}...'")

        try:
            response = requests.post(
                f"{self.api_url}/v1/chat/completions",
                json={
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "top_p": 0.8
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                timeout=1000
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"Raw response from Groq: {result}")

            if "choices" not in result or not result["choices"]:
                logger.error("No choices returned in Groq response.")
                return ""

            message = result["choices"][0].get("message", {})
            content = message.get("content", None)

            if content is None:
                logger.error("LLM response contains no message content.")
                return ""

            logger.info(f"LLM content: {content[:100]}...")
            return content.strip()

        except requests.exceptions.Timeout:
            logger.error("Groq API request timed out")
            return ""

        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request error: {e}")
            return ""

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ""


_raw_llm_client = LLMClient()

llm_client = RunnableLambda(
    lambda input: _raw_llm_client.predict(
        input.to_string() if isinstance(input, PromptValue) else str(input)
    )
)
