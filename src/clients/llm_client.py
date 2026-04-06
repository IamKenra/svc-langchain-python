import os
import requests
import logging
import threading
import time
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
        self.max_retries = int(os.getenv("GROQ_MAX_RETRIES", "2"))
        self.retry_base_delay_ms = int(os.getenv("GROQ_RETRY_BASE_DELAY_MS", "1500"))
        self.retry_max_delay_ms = int(os.getenv("GROQ_RETRY_MAX_DELAY_MS", "8000"))
        self.min_request_interval_ms = int(os.getenv("GROQ_MIN_REQUEST_INTERVAL_MS", "3000"))
        self._seq_lock = threading.Lock()
        self._last_response_at = 0.0

        if not self.api_key:
            raise ValueError("ERROR: GROQ_API_KEY tidak ditemukan!")

        logger.info(f"Using Groq Cloud at: {self.api_url}, model: {self.model_name}")

    def _wait_min_interval_locked(self) -> None:
        if self.min_request_interval_ms <= 0:
            return

        if self._last_response_at <= 0:
            return

        elapsed_ms = (time.monotonic() - self._last_response_at) * 1000.0
        wait_ms = self.min_request_interval_ms - elapsed_ms
        if wait_ms > 0:
            time.sleep(wait_ms / 1000.0)

    def _retry_delay_seconds(self, attempt: int) -> float:
        base = max(0, self.retry_base_delay_ms)
        delay_ms = base * (2 ** attempt)
        if self.retry_max_delay_ms > 0:
            delay_ms = min(delay_ms, self.retry_max_delay_ms)
        return max(0.0, delay_ms / 1000.0)

    def _is_retryable_status(self, status_code: int) -> bool:
        return status_code == 429 or status_code >= 500

    def predict(self, prompt: str) -> str:
        logger.info(f"Sending request to Groq API with model {self.model_name}: text='{prompt[:80]}...'")

        with self._seq_lock:
            self._wait_min_interval_locked()

            try:
                for attempt in range(self.max_retries + 1):
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
                            timeout=120
                        )

                        if response.status_code != 200:
                            body_preview = (response.text or "")[:300]
                            logger.error(
                                "Groq API non-200 status=%s attempt=%s body=%s",
                                response.status_code,
                                attempt + 1,
                                body_preview,
                            )
                            if attempt < self.max_retries and self._is_retryable_status(response.status_code):
                                time.sleep(self._retry_delay_seconds(attempt))
                                continue
                            return ""

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

                        content = content.strip()
                        if content == "":
                            logger.error("LLM response content is empty.")
                            if attempt < self.max_retries:
                                time.sleep(self._retry_delay_seconds(attempt))
                                continue
                            return ""

                        logger.info(f"LLM content: {content[:100]}...")
                        return content

                    except requests.exceptions.Timeout:
                        logger.error("Groq API request timed out (attempt=%s)", attempt + 1)
                        if attempt < self.max_retries:
                            time.sleep(self._retry_delay_seconds(attempt))
                            continue
                        return ""

                    except requests.exceptions.RequestException as e:
                        logger.error(f"Groq API request error (attempt={attempt + 1}): {e}")
                        if attempt < self.max_retries:
                            time.sleep(self._retry_delay_seconds(attempt))
                            continue
                        return ""

                    except Exception as e:
                        logger.error(f"Unexpected error in Groq request (attempt={attempt + 1}): {e}")
                        if attempt < self.max_retries:
                            time.sleep(self._retry_delay_seconds(attempt))
                            continue
                        return ""
            finally:
                self._last_response_at = time.monotonic()


_raw_llm_client = LLMClient()

llm_client = RunnableLambda(
    lambda input: _raw_llm_client.predict(
        input.to_string() if isinstance(input, PromptValue) else str(input)
    )
)
