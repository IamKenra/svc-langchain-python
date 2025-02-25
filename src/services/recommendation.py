from src.models.llm_client import llm_client
import logging
import json

logger = logging.getLogger(__name__)

def generate_recommendation(data):
    prompt = f"""
    Berikut adalah statistik performa server saat ini:
    - CPU Usage: {data.cpu_usage}%
    - RAM Usage: {data.ram_usage}%
    - Disk Usage: {data.disk_usage}%

    Berikan rekomendasi dalam format JSON **tanpa tambahan teks lain**:
    ```json
    {{
        "recommendations": [
            {{
                "title": "Judul Rekomendasi",
                "description": "Deskripsi lengkap rekomendasi"
            }}
        ],
        "summary": "Ringkasan rekomendasi untuk ditampilkan di notifikasi"
    }}
    ```
    Ingat! **Hanya output JSON, tanpa teks tambahan** di luar blok JSON.
    """

    logger.info(f"🔍 Generating recommendation using hosted Ollama API...")
    response = llm_client.predict(prompt).strip()

    # Coba parse JSON, jika gagal kembalikan error handler
    try:
        formatted_response = json.loads(response)
    except json.JSONDecodeError:
        logger.error("❌ Error: LLM output is not a valid JSON. Raw Output: " + response)
        formatted_response = {
            "recommendations": [{"title": "Error", "description": "LLM tidak mengembalikan format JSON yang valid."}],
            "summary": "Terjadi kesalahan dalam memproses rekomendasi."
        }

    return formatted_response
